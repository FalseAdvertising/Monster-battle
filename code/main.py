import pygame
import math
from settings import *
from support import *
from monster import Monster
from ui import BattleUI
from battle_engine import BattleEngine
from selection_screen import SelectionScreen  # Add this import

class LoadingScreen:
    def __init__(self, player1_monster, player2_monster):
        self.player1_monster = player1_monster
        self.player2_monster = player2_monster
        self.alpha = 0
        self.fade_speed = 2
        self.music_playing = False
        self.timer = 0
        self.duration = 3000  # 3 seconds
        # Load audio
        try:
            pygame.mixer.music.load('audio/halloween-spooky-music-413648.mp3')
        except Exception as e:
            print(f"Could not load loading music: {e}")

    def run(self, surface):
        # Start music if not playing
        if not self.music_playing:
            try:
                pygame.mixer.music.play(-1)  # Loop indefinitely
                self.music_playing = True
            except Exception as e:
                print(f"Could not play loading music: {e}")

        # Update timer
        self.timer += 16  # Approximate 60 FPS

        # Fade in/out effect
        self.alpha += self.fade_speed
        if self.alpha >= 255:
            self.fade_speed = -self.fade_speed
        elif self.alpha <= 0:
            self.fade_speed = -self.fade_speed

        # Draw background
        surface.fill((0, 0, 0))

        # Draw fading monster sprites
        p1_img = self.player1_monster.back_sprite
        p2_img = self.player2_monster.front_sprite

        # Scale and position
        scale = 0.8
        p1_scaled = pygame.transform.smoothscale(p1_img, (int(p1_img.get_width() * scale), int(p1_img.get_height() * scale)))
        p2_scaled = pygame.transform.smoothscale(p2_img, (int(p2_img.get_width() * scale), int(p2_img.get_height() * scale)))

        p1_rect = p1_scaled.get_rect(center=(WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2))
        p2_rect = p2_scaled.get_rect(center=(3 * WINDOW_WIDTH // 4, WINDOW_HEIGHT // 2))

        # Apply alpha
        p1_surf = pygame.Surface(p1_scaled.get_size(), pygame.SRCALPHA)
        p1_surf.blit(p1_scaled, (0, 0))
        p1_surf.set_alpha(self.alpha)
        surface.blit(p1_surf, p1_rect)

        p2_surf = pygame.Surface(p2_scaled.get_size(), pygame.SRCALPHA)
        p2_surf.blit(p2_scaled, (0, 0))
        p2_surf.set_alpha(self.alpha)
        surface.blit(p2_surf, p2_rect)

        # Draw loading text
        font = pygame.font.Font(None, 48)
        text = font.render("Loading Battle...", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 100))
        surface.blit(text, text_rect)

        pygame.display.update()

        # Check if duration has passed
        if self.timer >= self.duration:
            pygame.mixer.music.stop()
            return True

        # Check for quit or continue
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                pygame.mixer.music.stop()
                return True

        return None  # Continue loading

class Game:
    def __init__(self):
        pygame.init()
        
        # Run selection screen first
        selection = SelectionScreen()
        result = selection.run()
        
        if result is None:  # Window was closed during selection
            self.running = False
            return
            
        player1_choice, player2_choice = result  # Changed from ai_choice
        print(f"Player 1 selected: {player1_choice}")
        print(f"Player 2 selected: {player2_choice}")

        # Setup battle screen first for loading screen
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True
        self.battle_ended = False
        self.winner_name = None

        # Game states: 'selecting', 'executing'
        self.game_state = 'selecting'

        # Create monsters for loading screen
        self.player1_monster = Monster(player1_choice, (200, 470), is_player=True)
        self.player2_monster = Monster(player2_choice, (1000, 200), is_player=False)

        # Run loading screen
        loading = LoadingScreen(self.player1_monster, self.player2_monster)
        loading_result = None
        while loading_result is None:
            loading_result = loading.run(self.display_surface)
            if loading_result is False:  # Quit
                self.running = False
                return

        # Load background and floor
        try:
            self.background = pygame.image.load('images/other/bg.png').convert()
            self.floor = pygame.image.load('images/other/floor.png').convert_alpha()
        except Exception as e:
            print(f"Error loading background assets: {e}")
            self.background = None
            self.floor = None

        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.monster_group = pygame.sprite.Group()

        try:
            # Add to sprite groups
            self.monster_group.add(self.player1_monster, self.player2_monster)
            self.all_sprites.add(self.monster_group)

            # Create battle engine with both players
            self.battle_engine = BattleEngine(self.player1_monster, self.player2_monster)

            # Create UI with both players
            self.battle_ui = BattleUI(self.player1_monster, self.player2_monster)
            # Position monsters relative to UI floor if available so they sit on the platforms
            try:
                # Dynamic scaling and positioning for monsters
                def scale_and_position(monster, mid_x, panel_top, max_height, offset_above_panel=8):
                    # If sprite is too tall to fit above the panel, scale it down
                    img = monster.back_sprite if monster.is_player else monster.front_sprite
                    orig_w, orig_h = img.get_width(), img.get_height()
                    # Allow a little breathing room above the panel
                    available_height = panel_top - 20  # 20px margin from top
                    max_sprite_height = max_height
                    scale_factor = 1.0
                    if orig_h > max_sprite_height:
                        scale_factor = max_sprite_height / orig_h
                    # Never upscale, only downscale
                    scale_factor = min(scale_factor, 1.0)
                    new_w = int(orig_w * scale_factor)
                    new_h = int(orig_h * scale_factor)
                    # Rescale image if needed
                    if scale_factor < 1.0:
                        scaled_img = pygame.transform.smoothscale(img, (new_w, new_h))
                        monster.image = scaled_img
                        monster.rect = monster.image.get_rect()
                    else:
                        monster.image = img
                        monster.rect = monster.image.get_rect()
                    # Place midbottom just above the UI panel
                    monster.rect.midbottom = (mid_x, panel_top - offset_above_panel)
                    # If still not fitting (e.g. panel is too high), nudge up
                    if monster.rect.top < 10:
                        diff = 10 - monster.rect.top
                        monster.rect.y += diff

                left_mid = self.battle_ui.player1_floor_rect.centerx if getattr(self.battle_ui, 'player1_floor_rect', None) else 200
                right_mid = self.battle_ui.player2_floor_rect.centerx if getattr(self.battle_ui, 'player2_floor_rect', None) else 1000
                panel_top = self.battle_ui.left_rect.top
                # Allow monsters to fill up to 90% of the space above the panel
                max_sprite_height = panel_top - 20  # 20px margin from top
                scale_and_position(self.player1_monster, left_mid, panel_top, max_sprite_height)
                scale_and_position(self.player2_monster, right_mid, panel_top, max_sprite_height)
            except Exception as e:
                print(f"[Monster Positioning] Error: {e}")
                # fallback to original placement
                self.player1_monster.rect.center = (200, 470)
                self.player2_monster.rect.center = (1000, 200)
            print("Game elements created successfully")
        except Exception as e:
            print(f"Error creating game elements: {e}")
            self.running = False

    def handle_input(self):
        # Don't allow input if battle has ended
        if self.battle_ended:
            return

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]

        # Get moves from both players
        selected_action = self.battle_ui.handle_input(mouse_pos, mouse_click)

        if isinstance(selected_action, tuple):  # Only process when we have both moves
            player1_move, player2_move = selected_action
            print(f"\nNew turn starting:")
            print(f"Player 1 selected: {player1_move}")
            print(f"Player 2 selected: {player2_move}")

            # Execute the turn immediately
            winner = self.battle_engine.run_turn(player1_move, player2_move)

            # Update health display
            self.battle_ui.update_health_display(
                self.player1_monster.health,
                self.player2_monster.health
            )

            # Reset move selections for next turn
            self.battle_ui.reset_move_selections()

            if winner:
                self.battle_ended = True
                self.winner_name = winner.name
                player_num = "1" if winner == self.player1_monster else "2"
                print(f"Battle ended! Player {player_num} wins!")

    def update(self):
        self.all_sprites.update()

    def draw(self):
        # Draw background first
        if self.battle_ui.background:
            self.display_surface.blit(self.battle_ui.background, (0, 0))
        else:
            self.display_surface.fill(COLORS['white'])

        # Draw floors first (so panels can align correctly)
        if self.battle_ui.floor:
            self.display_surface.blit(self.battle_ui.floor, self.battle_ui.player1_floor_rect)
            self.display_surface.blit(self.battle_ui.floor, self.battle_ui.player2_floor_rect)

        # Draw UI panels behind monsters
        self.battle_ui.draw_panels(self.display_surface)

        # Draw monsters
        self.all_sprites.draw(self.display_surface)

        # Draw UI overlays (buttons, health bars) on top of monsters
        self.battle_ui.draw_overlay(self.display_surface)
        
        # Draw victory message if battle ended
        if self.battle_ended:
            self.draw_victory_message()
        
        pygame.display.update()



    def draw_victory_message(self):
        """Draw victory message in center of screen"""
        # Create semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.display_surface.blit(overlay, (0, 0))

        # Determine winner
        player_num = "1" if self.winner_name == self.player1_monster.name else "2"

        # Draw victory text
        font = pygame.font.Font(None, 100)
        victory_text = font.render(f"Player {player_num} Wins!", True, (255, 255, 255))
        text_rect = victory_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        self.display_surface.blit(victory_text, text_rect)

        # Draw monster name
        font_small = pygame.font.Font(None, 60)
        monster_text = font_small.render(f"{self.winner_name} is victorious!", True, (255, 215, 0))
        monster_rect = monster_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))
        self.display_surface.blit(monster_text, monster_rect)

    def run(self):
        while self.running:
            # Time
            dt = self.clock.tick(60) / 1000

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Input
            self.handle_input()

            # Update
            self.update()

            # Draw
            self.draw()

        pygame.quit()

if __name__ == '__main__':
    game = Game()
    game.run()