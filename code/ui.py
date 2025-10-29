import pygame
import os
import math
import random
from settings import *

class BattleUI:
    def __init__(self, player1_monster, player2_monster):
        # Theme colors map
        self.colors = {
            'white': COLORS['white'],
            'black': COLORS['black'],
            'gray': COLORS['gray'],
            'light_gray': COLORS['light_gray'],
            'dark_gray': COLORS['dark_gray'],
            'green': COLORS['green']
        }

        # Load battle background (prefer user-specified Battle-Ground.jpg)
        bg_candidates = [
            os.path.normpath(os.path.join('background', 'Battle-Ground.jpg')),
            'images/other/bg.png'
        ]
        self.background = None
        for p in bg_candidates:
            try:
                if os.path.exists(p):
                    self.background = pygame.image.load(p).convert()
                    self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    break
            except Exception:
                continue

        # Load floor image (optional)
        try:
            self.floor = pygame.image.load('images/other/floor.png').convert_alpha()
            self.player1_floor_rect = self.floor.get_rect(midtop=(200, 480))
            self.player2_floor_rect = self.floor.get_rect(midtop=(1000, 210))
        except Exception:
            self.floor = None

        # Adjust bottom rectangle height and monster position
        bottom_height = 250  # Increased from 200
        self.left_rect = pygame.Rect(0, WINDOW_HEIGHT - bottom_height, WINDOW_WIDTH // 2, bottom_height)
        self.right_rect = pygame.Rect(WINDOW_WIDTH // 2, WINDOW_HEIGHT - bottom_height, WINDOW_WIDTH // 2, bottom_height)

        # Draw dividing line
        self.divider_points = [
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT - bottom_height),
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT)
        ]
        
        # Animation state
        self.animation_timer = 0
        self.is_animating = False
        self.show_move_bar = True
        
        # Monster animation properties
        self.bob_time = 0
        self.bob_speed = 2
        self.bob_amplitude = 10
        self.monster1_offset_y = 0
        self.monster2_offset_y = 0
        
        # Hit animation properties
        self.monster1_hit_offset = 0
        self.monster2_hit_offset = 0
        self.hit_return_speed = 0.2
        self.max_hit_offset = 30
        
        # Load attack effects
        self.attack_sprites = {}
        self.attack_sounds = {}
        self.load_attack_effects()
        
        # Setup ability buttons for both players
        self.player1_buttons = []
        self.player2_buttons = []
        
        # Move selection tracking
        self.player1_selection = None
        self.player2_selection = None
        self.last_click = False

        # Health tracking
        self.player1_health = player1_monster.health
        self.player2_health = player2_monster.health
        self.player1_max_health = player1_monster.health
        self.player2_max_health = player2_monster.health

        # Play Again button setup
        self.play_again_button = None
        self.exit_button = None
        self.setup_end_game_buttons()

        # Font setup - use Creepster if available
        creepster_candidates = [
            os.path.normpath(os.path.join('background', 'Creepster-Regular.ttf')),
        ]
        creepster_path = None
        for p in creepster_candidates:
            if os.path.exists(p):
                creepster_path = p
                break

        if creepster_path:
            self.name_font = pygame.font.Font(creepster_path, 36)
            self.hp_font = pygame.font.Font(creepster_path, 20)
            self.ability_font = pygame.font.Font(creepster_path, 26)
        else:
            self.name_font = pygame.font.SysFont(None, 36)
            self.hp_font = pygame.font.SysFont(None, 20)
            self.ability_font = pygame.font.SysFont(None, 26)

        # Load wood texture for UI panels/buttons if present
        try:
            self.wood_texture = pygame.image.load('images/other/Wood_sign2.png').convert_alpha()
        except Exception:
            self.wood_texture = None

        # Optional skull/pumpkin icon for HP bar ends
        if os.path.exists('images/other/skull.png'):
            try:
                self.skull_icon = pygame.image.load('images/other/skull.png').convert_alpha()
            except Exception:
                self.skull_icon = None
        else:
            self.skull_icon = None

        # Particles (embers / mist)
        self.particles = []
        self.mist = []
        
        # Setup the ability buttons last (after loading fonts and textures)
        self.setup_ability_buttons(player1_monster.get_available_abilities(), player2_monster.get_available_abilities())
        
        # Store monster references for dynamic updates
        self.player1_monster_ref = player1_monster
        self.player2_monster_ref = player2_monster
        
        # Monster animation properties
        self.bob_time = 0
        self.bob_speed = 2
        self.bob_amplitude = 10
        self.monster1_offset_y = 0
        self.monster2_offset_y = 0
        
        # Hit animation properties
        self.monster1_hit_offset = 0
        self.monster2_hit_offset = 0
        self.hit_return_speed = 0.2
        self.max_hit_offset = 30
        
        # Load attack effects
        self.attack_sprites = {}
        self.attack_sounds = {}
        self.load_attack_effects()

        # Load battle background (prefer user-specified Battle-Ground.jpg)
        bg_candidates = [
            os.path.normpath(os.path.join('background', 'Battle-Ground.jpg')),
            'images/other/bg.png'
        ]
        self.background = None
        for p in bg_candidates:
            try:
                if os.path.exists(p):
                    self.background = pygame.image.load(p).convert()
                    self.background = pygame.transform.scale(self.background, (WINDOW_WIDTH, WINDOW_HEIGHT))
                    break
            except Exception:
                continue

        # Load floor image (optional)
        try:
            self.floor = pygame.image.load('images/other/floor.png').convert_alpha()
            self.player1_floor_rect = self.floor.get_rect(midtop=(200, 480))
            self.player2_floor_rect = self.floor.get_rect(midtop=(1000, 210))
        except Exception:
            self.floor = None

        # Adjust bottom rectangle height and monster position
        bottom_height = 250  # Increased from 200
        self.left_rect = pygame.Rect(0, WINDOW_HEIGHT - bottom_height, WINDOW_WIDTH // 2, bottom_height)
        self.right_rect = pygame.Rect(WINDOW_WIDTH // 2, WINDOW_HEIGHT - bottom_height, WINDOW_WIDTH // 2, bottom_height)

        # Draw dividing line
        self.divider_points = [
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT - bottom_height),
            (WINDOW_WIDTH // 2, WINDOW_HEIGHT)
        ]
        
    def setup_end_game_buttons(self):
        """Setup Play Again and Exit buttons for end game screen"""
        button_width = 200
        button_height = 60
        button_spacing = 40
        
        # Center the buttons horizontally and position them in lower portion of screen
        total_width = (button_width * 2) + button_spacing
        start_x = (WINDOW_WIDTH - total_width) // 2
        button_y = WINDOW_HEIGHT // 2 + 120
        
        self.play_again_button = {
            'rect': pygame.Rect(start_x, button_y, button_width, button_height),
            'text': 'Play Again',
            'hover': False
        }
        
        self.exit_button = {
            'rect': pygame.Rect(start_x + button_width + button_spacing, button_y, button_width, button_height),
            'text': 'Back to Menu',
            'hover': False
        }

    def load_attack_effects(self):
        """Load all attack images and sounds"""
        # Load attack sprites
        attack_types = ['fire', 'ice', 'scratch', 'explosion', 'green', 'splash']
        for attack in attack_types:
            try:
                img_path = os.path.join('images', 'attacks', f'{attack}.png')
                self.attack_sprites[attack] = pygame.image.load(img_path).convert_alpha()
            except Exception as e:
                print(f"Failed to load attack sprite {attack}: {e}")
        
        # Load attack sounds
        for attack in attack_types:
            try:
                sound_path = os.path.join('audio', f'{attack}.wav')
                if not os.path.exists(sound_path):
                    sound_path = os.path.join('audio', f'{attack}.mp3')
                self.attack_sounds[attack] = pygame.mixer.Sound(sound_path)
            except Exception as e:
                print(f"Failed to load attack sound {attack}: {e}")
                
    def update_animations(self, dt):
        """Update all animation states"""
        # Update bobbing animation
        self.bob_time += dt * self.bob_speed
        self.monster1_offset_y = math.sin(self.bob_time) * self.bob_amplitude
        self.monster2_offset_y = math.sin(self.bob_time + math.pi) * self.bob_amplitude
        
        # Update hit reactions
        if self.monster1_hit_offset > 0:
            self.monster1_hit_offset *= (1 - self.hit_return_speed)
        if self.monster2_hit_offset > 0:
            self.monster2_hit_offset *= (1 - self.hit_return_speed)
            
        # Update attack animation timer
        if self.is_animating:
            self.animation_timer += dt
            if self.animation_timer >= 1.0:
                self.is_animating = False
                self.show_move_bar = True
                self.animation_timer = 0
                
    def play_attack_animation(self, attacker_is_player1, move_name):
        """Start an attack animation sequence"""
        # Determine animation type based on move name
        anim_type = self.get_animation_type(move_name)
        if anim_type in self.attack_sprites:
            # Play sound effect - REMOVED for attack sounds only
            # if anim_type in self.attack_sounds:
            #     self.attack_sounds[anim_type].play()

            # Set animation state
            self.is_animating = True
            self.show_move_bar = False
            self.animation_timer = 0

            # Apply hit reaction to target
            if attacker_is_player1:
                self.monster2_hit_offset = self.max_hit_offset
            else:
                self.monster1_hit_offset = self.max_hit_offset
                
    def get_animation_type(self, move_name):
        """Map move names to animation types"""
        move_name = move_name.lower()
        if 'fire' in move_name:
            return 'fire'
        elif 'ice' in move_name or 'freeze' in move_name:
            return 'ice'
        elif 'scratch' in move_name or 'claw' in move_name:
            return 'scratch'
        elif 'explosion' in move_name or 'blast' in move_name:
            return 'explosion'
        elif 'leaf' in move_name or 'grass' in move_name:
            return 'green'
        elif 'water' in move_name or 'splash' in move_name:
            return 'splash'
        return 'scratch'  # default animation



    def refresh_ability_buttons(self):
        """Refresh ability buttons to reflect used special moves"""
        # Clear existing buttons
        self.player1_buttons.clear()
        self.player2_buttons.clear()
        
        # Recreate buttons with current available abilities
        self.setup_ability_buttons(
            self.player1_monster_ref.get_available_abilities(), 
            self.player2_monster_ref.get_available_abilities()
        )

    def setup_ability_buttons(self, player1_abilities, player2_abilities):
        # Calculate button dimensions for 2x2 grid with more space
        padding = 30  # Increased padding
        grid_width = (self.left_rect.width - (3 * padding)) // 2
        grid_height = (self.left_rect.height - (4 * padding)) // 2  # More vertical space

    # Setup player 1 buttons (left side)
        for i, ability in enumerate(player1_abilities[:4]):
            row = i // 2
            col = i % 2
            x = self.left_rect.left + padding + (col * (grid_width + padding))
            y = self.left_rect.top + padding + (row * (grid_height + padding))
            
            # Check if this is a special move
            is_special = ability in ABILITIES_DATA and ABILITIES_DATA[ability].get('type') == 'special'
            
            self.player1_buttons.append({
                'rect': pygame.Rect(x, y, grid_width, grid_height),
                'ability': ability,
                'color': self.colors['white'],
                'hover': False,
                'locked': False,
                'is_special': is_special
            })

    # Setup player 2 buttons (right side)
        for i, ability in enumerate(player2_abilities[:4]):
            row = i // 2
            col = i % 2
            x = self.right_rect.left + padding + (col * (grid_width + padding))
            y = self.right_rect.top + padding + (row * (grid_height + padding))
            
            # Check if this is a special move
            is_special = ability in ABILITIES_DATA and ABILITIES_DATA[ability].get('type') == 'special'
            
            self.player2_buttons.append({
                'rect': pygame.Rect(x, y, grid_width, grid_height),
                'ability': ability,
                'color': self.colors['white'],
                'hover': False,
                'locked': False,
                'is_special': is_special
            })

    def handle_end_game_input(self, mouse_pos, mouse_click):
        """Handle input for end game buttons"""
        if not mouse_click:
            return None
            
        # Check Play Again button
        if self.play_again_button['rect'].collidepoint(mouse_pos):
            return 'play_again'
            
        # Check Exit button
        if self.exit_button['rect'].collidepoint(mouse_pos):
            return 'exit'
            
        return None

    def update_end_game_hover(self, mouse_pos):
        """Update hover states for end game buttons"""
        self.play_again_button['hover'] = self.play_again_button['rect'].collidepoint(mouse_pos)
        self.exit_button['hover'] = self.exit_button['rect'].collidepoint(mouse_pos)

    def handle_input(self, mouse_pos, mouse_click):
        """Handle mouse input for move selection with deselection capability"""
        if not mouse_click and self.last_click:
            # Check player 1 buttons
            for button in self.player1_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    if button['locked']:
                        # Deselect if clicking already selected move
                        button['locked'] = False
                        self.player1_selection = None
                        print("Player 1 deselected move")
                    elif not self.player1_selection:
                        # Select new move if none selected
                        self.player1_selection = button['ability']
                        button['locked'] = True
                        print("Player 1 selected:", button['ability'])

            # Check player 2 buttons
            for button in self.player2_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    if button['locked']:
                        # Deselect if clicking already selected move
                        button['locked'] = False
                        self.player2_selection = None
                        print("Player 2 deselected move")
                    elif not self.player2_selection:
                        # Select new move if none selected
                        self.player2_selection = button['ability']
                        button['locked'] = True
                        print("Player 2 selected:", button['ability'])

            # Return both moves only if both players have selected
            if self.player1_selection and self.player2_selection:
                moves = (self.player1_selection, self.player2_selection)
                return moves

        self.last_click = mouse_click
        return None

    def update_health_display(self, player1_health, player2_health):
        """Update the stored health values for display"""
        # Clamp health to minimum of 0
        self.player1_health = max(0, player1_health)
        self.player2_health = max(0, player2_health)

        
    # Add to BattleUI class in ui.py
    def reset_move_selections(self):
        """Reset all move selections after a turn"""
        self.player1_selection = None
        self.player2_selection = None
        for button in self.player1_buttons + self.player2_buttons:
            button['locked'] = False
            button['hover'] = False
    
    def draw(self, surface, player1_monster, player2_monster):
        """Draw the complete battle UI with animations"""
        # Draw background
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(self.colors['white'])

        # Draw floor images if available
        if self.floor:
            surface.blit(self.floor, self.player1_floor_rect)
            surface.blit(self.floor, self.player2_floor_rect)

        # Apply animation offsets to monster positions
        monster1_rect = player1_monster.rect.copy()
        monster2_rect = player2_monster.rect.copy()
        
        # Apply bobbing animation
        monster1_rect.y += self.monster1_offset_y
        monster2_rect.y += self.monster2_offset_y
        
        # Apply hit reactions
        monster1_rect.x -= self.monster1_hit_offset
        monster2_rect.x += self.monster2_hit_offset
        
        # Draw monsters with current positions
        surface.blit(player1_monster.image, monster1_rect)
        surface.blit(player2_monster.image, monster2_rect)

        # Draw UI panels and particles
        self.draw_panels(surface)

        # Only draw the move selection UI if not animating
        if self.show_move_bar:
            self.draw_overlay(surface)

    def draw_panels(self, surface):
        """Draw background UI panels behind monsters (wood panels, particles)."""
        # Draw subtle particles (embers/mist)
        # Spawn ember occasionally
        if random.random() < 0.02:
            self.particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT//2),
                'r': random.randint(2, 5),
                'vy': random.uniform(0.1, 0.6),
                'alpha': 255
            })
        # Update and draw embers
        for p in list(self.particles):
            p['y'] += p['vy']
            p['alpha'] -= 1.2
            if p['alpha'] <= 0 or p['y'] > WINDOW_HEIGHT:
                self.particles.remove(p)
                continue
            s = pygame.Surface((p['r']*2, p['r']*2), pygame.SRCALPHA)
            s.fill((0,0,0,0))
            pygame.draw.circle(s, (255, 140, 20, int(p['alpha'])), (p['r'], p['r']), p['r'])
            surface.blit(s, (p['x']-p['r'], p['y']-p['r']))

        # Draw bottom rectangles (UI panels) - use wood texture if available
        if self.wood_texture:
            left_bg = pygame.transform.smoothscale(self.wood_texture, (self.left_rect.width, self.left_rect.height))
            right_bg = pygame.transform.smoothscale(self.wood_texture, (self.right_rect.width, self.right_rect.height))
            surface.blit(left_bg, self.left_rect.topleft)
            surface.blit(right_bg, self.right_rect.topleft)
            # subtle frame
            pygame.draw.rect(surface, (30,20,10), self.left_rect, 6, border_radius=8)
            pygame.draw.rect(surface, (30,20,10), self.right_rect, 6, border_radius=8)
        else:
            pygame.draw.rect(surface, COLORS['gray'], self.left_rect)
            pygame.draw.rect(surface, COLORS['gray'], self.right_rect)

        # Draw dividing line (dotted)
        for y in range(self.divider_points[0][1], self.divider_points[1][1], 10):
            start_pos = (self.divider_points[0][0], y)
            end_pos = (self.divider_points[0][0], y + 5)
            pygame.draw.line(surface, self.colors['black'], start_pos, end_pos, 2)

    def draw_overlay(self, surface):
        """Draw foreground UI (labels, buttons, health bars) on top of monsters."""
        # Draw player labels (use themed font with outline) - positioned at bottom of panels
        p1_label = "Player 1" + (" (Locked)" if self.player1_selection else "")
        p2_label = "Player 2" + (" (Locked)" if self.player2_selection else "")
        # outline / shadow
        p1_shadow = self.name_font.render(p1_label, True, (0,0,0))
        p2_shadow = self.name_font.render(p2_label, True, (0,0,0))
        surface.blit(p1_shadow, (self.left_rect.centerx - p1_shadow.get_width()//2 + 2, self.left_rect.bottom - 38))
        surface.blit(p2_shadow, (self.right_rect.centerx - p2_shadow.get_width()//2 + 2, self.right_rect.bottom - 38))
        p1_text = self.name_font.render(p1_label, True, (255,180,80))
        p2_text = self.name_font.render(p2_label, True, (255,180,80))
        surface.blit(p1_text, (self.left_rect.centerx - p1_text.get_width()//2, self.left_rect.bottom - 40))
        surface.blit(p2_text, (self.right_rect.centerx - p2_text.get_width()//2, self.right_rect.bottom - 40))

        # Draw player 1 buttons
        for button in self.player1_buttons:
            rect = button['rect']
            if self.wood_texture:
                btn_bg = pygame.transform.smoothscale(self.wood_texture, (rect.width, rect.height))
                surface.blit(btn_bg, rect.topleft)
            else:
                pygame.draw.rect(surface, self.colors['white'], rect, border_radius=10)
            # glow if hover/locked, special color for special moves
            if button['locked']:
                pygame.draw.rect(surface, (255,120,20), rect, 4, border_radius=10)
            elif button['hover']:
                pygame.draw.rect(surface, (180,0,255), rect, 3, border_radius=10)
            elif button.get('is_special', False):
                pygame.draw.rect(surface, (255,215,0), rect, 3, border_radius=10)  # Gold border for special moves
            # ability text
            text_color = (255,255,100) if button.get('is_special', False) else (250,240,200)  # Golden text for special moves
            text_shadow = self.ability_font.render(button['ability'], True, (0,0,0))
            surface.blit(text_shadow, (rect.centerx - text_shadow.get_width()//2 + 1, rect.centery - text_shadow.get_height()//2 + 1))
            text = self.ability_font.render(button['ability'], True, text_color)
            surface.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))

        # Draw player 2 buttons
        for button in self.player2_buttons:
            rect = button['rect']
            if self.wood_texture:
                btn_bg = pygame.transform.smoothscale(self.wood_texture, (rect.width, rect.height))
                surface.blit(btn_bg, rect.topleft)
            else:
                pygame.draw.rect(surface, self.colors['white'], rect, border_radius=10)
            if button['locked']:
                pygame.draw.rect(surface, (255,120,20), rect, 4, border_radius=10)
            elif button['hover']:
                pygame.draw.rect(surface, (180,0,255), rect, 3, border_radius=10)
            elif button.get('is_special', False):
                pygame.draw.rect(surface, (255,215,0), rect, 3, border_radius=10)  # Gold border for special moves
            text_color = (255,255,100) if button.get('is_special', False) else (250,240,200)  # Golden text for special moves
            text_shadow = self.ability_font.render(button['ability'], True, (0,0,0))
            surface.blit(text_shadow, (rect.centerx - text_shadow.get_width()//2 + 1, rect.centery - text_shadow.get_height()//2 + 1))
            text = self.ability_font.render(button['ability'], True, text_color)
            surface.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))

        # Draw health bars (themed pumpkin/blood style)
        health_width = 200
        health_height = 22
        # Player 1
        p1_x = 50
        p1_y = 50
        p1_bg = pygame.Rect(p1_x, p1_y, health_width, health_height)
        p1_fill_w = int(health_width * (self.player1_health / max(1, self.player1_max_health)))
        p1_fill = pygame.Rect(p1_x, p1_y, p1_fill_w, health_height)
        # Player 2
        p2_x = WINDOW_WIDTH - 250
        p2_y = 50
        p2_bg = pygame.Rect(p2_x, p2_y, health_width, health_height)
        p2_fill_w = int(health_width * (self.player2_health / max(1, self.player2_max_health)))
        p2_fill = pygame.Rect(p2_x, p2_y, p2_fill_w, health_height)

        # Backgrounds
        pygame.draw.rect(surface, (40, 30, 30), p1_bg, border_radius=6)
        pygame.draw.rect(surface, (40, 30, 30), p2_bg, border_radius=6)

        # Fill colors (pumpkin orange); if low HP use blood red
        def fill_color(health, max_h):
            ratio = health / max(1, max_h)
            if ratio < 0.25:
                return (180, 30, 30)
            return (255, 140, 0)

        pygame.draw.rect(surface, fill_color(self.player1_health, self.player1_max_health), p1_fill, border_radius=6)
        pygame.draw.rect(surface, fill_color(self.player2_health, self.player2_max_health), p2_fill, border_radius=6)

        # Simple dripping effect along the filled part
        def draw_drips(fill_rect):
            if fill_rect.width <= 0:
                return
            drip_surf = pygame.Surface((fill_rect.width, 12), pygame.SRCALPHA)
            for i in range(0, fill_rect.width, 20):
                w = random.randint(6, 12)
                h = random.randint(4, 10)
                pygame.draw.ellipse(drip_surf, (255,120,20,180), (i, 6, w, h))
            surface.blit(drip_surf, (fill_rect.x, fill_rect.bottom - 6))

        draw_drips(p1_fill)
        draw_drips(p2_fill)

        # Draw skull/pumpkin icon at the end of the bar if available
        if self.skull_icon:
            icon_h = health_height + 6
            icon = pygame.transform.smoothscale(self.skull_icon, (icon_h, icon_h))
            surface.blit(icon, (p1_bg.right + 8, p1_bg.top - 3))
            surface.blit(icon, (p2_bg.right + 8, p2_bg.top - 3))

        # Draw HP text with outline for readability
        hp1_label = f"{int(self.player1_health)}/{self.player1_max_health}"
        hp2_label = f"{int(self.player2_health)}/{self.player2_max_health}"
        shadow1 = self.hp_font.render(hp1_label, True, (0,0,0))
        shadow2 = self.hp_font.render(hp2_label, True, (0,0,0))
        surface.blit(shadow1, (p1_x + 2, p1_y + health_height + 6))
        surface.blit(shadow2, (p2_x + 2, p2_y + health_height + 6))
        hp1_text = self.hp_font.render(hp1_label, True, (255,255,255))
        hp2_text = self.hp_font.render(hp2_label, True, (255,255,255))
        surface.blit(hp1_text, (p1_x, p1_y + health_height + 4))
        surface.blit(hp2_text, (p2_x, p2_y + health_height + 4))
        
        # Draw status effect indicators
        self.draw_status_effects(surface)

    def draw_status_effects(self, surface):
        """Draw status effect indicators for both players"""
        # Status effect positions (under health bars)
        p1_status_x = 50
        p1_status_y = 100
        p2_status_x = WINDOW_WIDTH - 250
        p2_status_y = 100
        
        # Player 1 status effects
        status_offset = 0
        if hasattr(self.player1_monster_ref, 'shield_active') and self.player1_monster_ref.shield_active:
            shield_text = self.hp_font.render("🛡️ SHIELD", True, (0, 255, 255))
            surface.blit(shield_text, (p1_status_x, p1_status_y + status_offset))
            status_offset += 25
            
        if hasattr(self.player1_monster_ref, 'burn_turns') and self.player1_monster_ref.burn_turns > 0:
            burn_text = self.hp_font.render(f"🔥 BURN ({self.player1_monster_ref.burn_turns})", True, (255, 100, 0))
            surface.blit(burn_text, (p1_status_x, p1_status_y + status_offset))
            
        # Player 2 status effects
        status_offset = 0
        if hasattr(self.player2_monster_ref, 'shield_active') and self.player2_monster_ref.shield_active:
            shield_text = self.hp_font.render("🛡️ SHIELD", True, (0, 255, 255))
            surface.blit(shield_text, (p2_status_x, p2_status_y + status_offset))
            status_offset += 25
            
        if hasattr(self.player2_monster_ref, 'burn_turns') and self.player2_monster_ref.burn_turns > 0:
            burn_text = self.hp_font.render(f"🔥 BURN ({self.player2_monster_ref.burn_turns})", True, (255, 100, 0))
            surface.blit(burn_text, (p2_status_x, p2_status_y + status_offset))

    def draw_end_game_buttons(self, surface):
        """Draw Play Again and Exit buttons"""
        for button in [self.play_again_button, self.exit_button]:
            rect = button['rect']
            
            # Draw button background with wood texture if available
            if self.wood_texture:
                btn_bg = pygame.transform.smoothscale(self.wood_texture, (rect.width, rect.height))
                surface.blit(btn_bg, rect.topleft)
            else:
                pygame.draw.rect(surface, self.colors['white'], rect, border_radius=10)
            
            # Draw button border with glow effect if hovered
            border_color = (255, 120, 20) if button['hover'] else (100, 80, 60)
            pygame.draw.rect(surface, border_color, rect, 4, border_radius=10)
            
            # Draw button text with shadow
            text_shadow = self.ability_font.render(button['text'], True, (0, 0, 0))
            surface.blit(text_shadow, (rect.centerx - text_shadow.get_width()//2 + 2, rect.centery - text_shadow.get_height()//2 + 2))
            
            text_color = (255, 255, 255) if button['hover'] else (250, 240, 200)
            text = self.ability_font.render(button['text'], True, text_color)
            surface.blit(text, (rect.centerx - text.get_width()//2, rect.centery - text.get_height()//2))