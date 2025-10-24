import pygame
from settings import *

class BattleUI:
    def __init__(self, player_monster, enemy_monster):
        # Load background and floors
        try:
            self.background = pygame.image.load('images/other/bg.png').convert()
            self.floor = pygame.image.load('images/other/floor.png').convert_alpha()
            
            # Get monster positions
            player_pos = player_monster.rect.midbottom
            enemy_pos = enemy_monster.rect.midbottom
            
            # Update player floor Y position (460 + 20 = 480)
            self.player_floor_rect = self.floor.get_rect(midtop=(200, 480))  # Player floor
            self.enemy_floor_rect = self.floor.get_rect(midtop=(1000, 210))  # Enemy floor
            
        except Exception as e:
            print(f"Error loading UI assets: {e}")
            self.background = None
            self.floor = None

        # Bottom rectangle setup (20% of screen height)
        bottom_height = int(WINDOW_HEIGHT * 0.2)  # 200px in 1000px height
        self.bottom_rect = pygame.Rect(
            0,  # 0% from left
            WINDOW_HEIGHT - bottom_height,  # 80% from top
            WINDOW_WIDTH,  # 100% width
            bottom_height  # 20% height
        )
        self.bottom_color = COLORS['gray']

        # Split bottom rectangle into two halves
        self.left_rect = pygame.Rect(
            0,  # Left side
            WINDOW_HEIGHT - bottom_height,
            WINDOW_WIDTH // 2,  # Half width
            bottom_height
        )
        
        self.right_rect = pygame.Rect(
            WINDOW_WIDTH // 2,  # Right side
            WINDOW_HEIGHT - bottom_height,
            WINDOW_WIDTH // 2,  # Half width
            bottom_height
        )

        # Ability rectangles setup
        self.ability_rects = []
        self.ability_spacing = int(WINDOW_WIDTH * 0.02)  # 2% of screen width
        self.ability_size = (
            int(WINDOW_WIDTH * 0.15),  # 15% of screen width
            int(bottom_height * 0.25)   # 25% of bottom rectangle height
        )
        self.setup_ability_rects(player_monster.abilities)

        # Ability buttons setup
        self.player_buttons = []
        self.enemy_buttons = []
        self.setup_ability_grid(player_monster.abilities, enemy_monster.abilities)

        # Font setup - scale with screen height
        self.font = pygame.font.Font(None, int(bottom_height * 0.15))  # 15% of bottom height

        # Health variables
        self.player_health = 100
        self.enemy_health = 100

        # Add end game button at top center
        button_width = 200
        button_height = 50
        self.end_button = {
            'rect': pygame.Rect(
                (WINDOW_WIDTH - button_width) // 2,  # Center horizontally
                20,  # 20px from top
                button_width,
                button_height
            ),
            'color': COLORS['red'],
            'hover': False,
            'text': 'End Game'
        }

    def setup_ability_rects(self, abilities):
        # Calculate starting position to center abilities
        ability_total_width = (len(abilities) * self.ability_size[0] + 
                             (len(abilities) - 1) * self.ability_spacing)
        start_x = (WINDOW_WIDTH - ability_total_width) // 2

        # Create rectangle for each ability - vertically centered in bottom rect
        ability_y = self.bottom_rect.top + (self.bottom_rect.height - self.ability_size[1]) // 2
        
        for i, ability in enumerate(abilities):
            x = start_x + i * (self.ability_size[0] + self.ability_spacing)
            rect = pygame.Rect(x, ability_y, *self.ability_size)
            self.ability_rects.append((rect, ability))

    def setup_ability_grid(self, player_abilities, enemy_abilities):
        # Calculate button dimensions for 2x2 grid
        padding = 20  # Space between buttons
        grid_width = (self.left_rect.width - (3 * padding)) // 2  # 2 columns
        grid_height = (self.left_rect.height - (3 * padding)) // 2  # 2 rows

        # Setup player ability buttons (left side)
        for i, ability in enumerate(player_abilities[:4]):  # Limit to 4 abilities
            row = i // 2
            col = i % 2
            x = self.left_rect.left + padding + (col * (grid_width + padding))
            y = self.left_rect.top + padding + (row * (grid_height + padding))
            
            rect = pygame.Rect(x, y, grid_width, grid_height)
            self.player_buttons.append({
                'rect': rect,
                'ability': ability,
                'color': COLORS['white'],
                'hover': False
            })

        # Setup enemy ability buttons (right side)
        for i, ability in enumerate(enemy_abilities[:4]):  # Limit to 4 abilities
            row = i // 2
            col = i % 2
            x = self.right_rect.left + padding + (col * (grid_width + padding))
            y = self.right_rect.top + padding + (row * (grid_height + padding))
            
            rect = pygame.Rect(x, y, grid_width, grid_height)
            self.enemy_buttons.append({
                'rect': rect,
                'ability': ability,
                'color': COLORS['gray'],  # Different color for enemy abilities
                'hover': False,
                'enabled': False  # Enemy buttons are disabled
            })

    def handle_input(self, mouse_pos, mouse_click):
        # Check end game button first
        if self.end_button['rect'].collidepoint(mouse_pos):
            self.end_button['hover'] = True
            if mouse_click:
                return 'end_game'
        else:
            self.end_button['hover'] = False

        # Check ability buttons
        for button in self.player_buttons:
            button['hover'] = button['rect'].collidepoint(mouse_pos)
            if button['hover'] and mouse_click:
                return button['ability']
        
        return None

    def update_health_display(self, player_health, enemy_health):
        """Update health display for both monsters"""
        self.player_health = player_health
        self.enemy_health = enemy_health

    def draw(self, surface):
        # Draw background
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(COLORS['white'])
        
        # Draw both floors
        if self.floor:
            surface.blit(self.floor, self.player_floor_rect)
            surface.blit(self.floor, self.enemy_floor_rect)

        # Draw bottom rectangle split
        pygame.draw.rect(surface, COLORS['gray'], self.left_rect)
        pygame.draw.rect(surface, COLORS['dark_gray'], self.right_rect)

        # Draw player ability buttons
        for button in self.player_buttons:
            color = COLORS['light_gray'] if button['hover'] else COLORS['white']
            pygame.draw.rect(surface, color, button['rect'], border_radius=10)
            
            text = self.font.render(button['ability'], True, COLORS['black'])
            text_rect = text.get_rect(center=button['rect'].center)
            surface.blit(text, text_rect)

        # Draw enemy ability buttons (disabled)
        for button in self.enemy_buttons:
            pygame.draw.rect(surface, button['color'], button['rect'], border_radius=10)
            
            text = self.font.render(button['ability'], True, COLORS['dark_gray'])
            text_rect = text.get_rect(center=button['rect'].center)
            surface.blit(text, text_rect)

        # Draw health bars
        player_health_rect = pygame.Rect(50, 50, 200 * (self.player_health/100), 20)
        enemy_health_rect = pygame.Rect(WINDOW_WIDTH-250, 50, 200 * (self.enemy_health/100), 20)
        
        pygame.draw.rect(surface, COLORS['red'], player_health_rect)
        pygame.draw.rect(surface, COLORS['red'], enemy_health_rect)

        # Draw end game button
        color = COLORS['dark_red'] if self.end_button['hover'] else COLORS['red']
        pygame.draw.rect(surface, color, self.end_button['rect'], border_radius=10)
        
        # Draw button text
        text = self.font.render(self.end_button['text'], True, COLORS['white'])
        text_rect = text.get_rect(center=self.end_button['rect'].center)
        surface.blit(text, text_rect)