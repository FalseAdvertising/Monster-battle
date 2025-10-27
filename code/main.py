import pygame
from settings import *
from support import *
from timer import Timer
from monster import Monster
from ui import BattleUI
from battle_engine import BattleEngine
from selection_screen import SelectionScreen  # Add this import

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
        
        # Setup battle screen
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True
        self.battle_ended = False
        self.winner_name = None

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
            # Create monsters with selected choices
            self.player1_monster = Monster(player1_choice, (200, 470), is_player=True)
            self.player2_monster = Monster(player2_choice, (1000, 200), is_player=False)
            
            # Add to sprite groups
            self.monster_group.add(self.player1_monster, self.player2_monster)
            self.all_sprites.add(self.monster_group)
            
            # Create battle engine with both players
            self.battle_engine = BattleEngine(self.player1_monster, self.player2_monster)
            
            # Create UI with both players
            self.battle_ui = BattleUI(self.player1_monster, self.player2_monster)
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
            
            # Execute turn
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

        # Draw floors
        if self.battle_ui.floor:
            self.display_surface.blit(self.battle_ui.floor, self.battle_ui.player1_floor_rect)
            self.display_surface.blit(self.battle_ui.floor, self.battle_ui.player2_floor_rect)
        
        # Draw monsters BEFORE UI rectangles
        self.all_sprites.draw(self.display_surface)
        
        # Draw UI elements (rectangles, buttons, health bars)
        self.battle_ui.draw(self.display_surface)
        
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