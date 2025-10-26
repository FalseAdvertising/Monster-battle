import pygame
from settings import *

class BattleUI:
    def __init__(self, player1_monster, player2_monster):
        # Add debug print to verify colors are loaded
        print("Available colors:", list(COLORS.keys()))
        
        # Store colors as instance variables to ensure availability
        self.colors = {
            'white': COLORS['white'],
            'black': COLORS['black'],
            'gray': COLORS['gray'],
            'light_gray': COLORS['light_gray'],
            'dark_gray': COLORS['dark_gray'],
            'green': COLORS['green']
        }
        
        # Load background and floor
        try:
            self.background = pygame.image.load('images/other/bg.png').convert()
            self.floor = pygame.image.load('images/other/floor.png').convert_alpha()
            
            # Floor positions
            self.player1_floor_rect = self.floor.get_rect(midtop=(200, 480))
            self.player2_floor_rect = self.floor.get_rect(midtop=(1000, 210))
        except Exception as e:
            print(f"Error loading UI assets: {e}")
            self.background = None
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

        # Adjust monster positions
        player1_monster.rect.centery = 400  # Moved up from 470
        
        # Setup ability buttons for both players
        self.player1_buttons = []
        self.player2_buttons = []
        self.setup_ability_buttons(player1_monster.abilities, player2_monster.abilities)

        # Move selection tracking
        self.player1_selection = None
        self.player2_selection = None
        self.last_click = False

        # Font setup
        self.font = pygame.font.Font(None, 36)

        # Add health tracking
        self.player1_health = player1_monster.health
        self.player2_health = player2_monster.health
        
        # Store max health for health bar calculations
        self.player1_max_health = player1_monster.health
        self.player2_max_health = player2_monster.health

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
            
            self.player1_buttons.append({
                'rect': pygame.Rect(x, y, grid_width, grid_height),
                'ability': ability,
                'color': self.colors['white'],
                'hover': False,
                'locked': False
            })

        # Setup player 2 buttons (right side)
        for i, ability in enumerate(player2_abilities[:4]):
            row = i // 2
            col = i % 2
            x = self.right_rect.left + padding + (col * (grid_width + padding))
            y = self.right_rect.top + padding + (row * (grid_height + padding))
            
            self.player2_buttons.append({
                'rect': pygame.Rect(x, y, grid_width, grid_height),
                'ability': ability,
                'color': self.colors['white'],
                'hover': False,
                'locked': False
            })

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
        self.player1_health = player1_health
        self.player2_health = player2_health

        
    # Add to BattleUI class in ui.py
    def reset_move_selections(self):
        """Reset all move selections after a turn"""
        self.player1_selection = None
        self.player2_selection = None
        for button in self.player1_buttons + self.player2_buttons:
            button['locked'] = False
            button['hover'] = False
    
    def draw(self, surface):
        # Draw background
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(COLORS['white'])

        # Draw floors
        if self.floor:
            surface.blit(self.floor, self.player1_floor_rect)
            surface.blit(self.floor, self.player2_floor_rect)

        # Draw bottom rectangles
        pygame.draw.rect(surface, COLORS['gray'], self.left_rect)
        pygame.draw.rect(surface, COLORS['gray'], self.right_rect)

        # Draw dividing line (dotted)
        for y in range(self.divider_points[0][1], self.divider_points[1][1], 10):
            start_pos = (self.divider_points[0][0], y)
            end_pos = (self.divider_points[0][0], y + 5)
            pygame.draw.line(surface, self.colors['black'], start_pos, end_pos, 2)

        # Draw player labels
        p1_text = self.font.render("Player 1" + (" (Locked)" if self.player1_selection else ""), True, COLORS['black'])
        p2_text = self.font.render("Player 2" + (" (Locked)" if self.player2_selection else ""), True, COLORS['black'])
        surface.blit(p1_text, (self.left_rect.centerx - p1_text.get_width()//2, self.left_rect.top + 10))
        surface.blit(p2_text, (self.right_rect.centerx - p2_text.get_width()//2, self.right_rect.top + 10))

        # Draw player 1 buttons
        for button in self.player1_buttons:
            color = (self.colors['green'] if button['locked'] 
                    else (self.colors['light_gray'] if button['hover'] 
                    else self.colors['white']))
            pygame.draw.rect(surface, color, button['rect'], border_radius=10)
            text = self.font.render(button['ability'], True, self.colors['black'])
            text_rect = text.get_rect(center=button['rect'].center)
            surface.blit(text, text_rect)

        # Draw player 2 buttons
        for button in self.player2_buttons:
            color = (self.colors['green'] if button['locked'] 
                    else (self.colors['light_gray'] if button['hover'] 
                    else self.colors['white']))
            pygame.draw.rect(surface, color, button['rect'], border_radius=10)
            text = self.font.render(button['ability'], True, self.colors['black'])
            text_rect = text.get_rect(center=button['rect'].center)
            surface.blit(text, text_rect)

        # Draw health bars
        # Player 1 health bar
        health_width = 200
        health_height = 20
        p1_health_rect = pygame.Rect(50, 50, health_width * (self.player1_health/self.player1_max_health), health_height)
        p1_health_bg = pygame.Rect(50, 50, health_width, health_height)
        
        # Player 2 health bar
        p2_health_rect = pygame.Rect(WINDOW_WIDTH-250, 50, health_width * (self.player2_health/self.player2_max_health), health_height)
        p2_health_bg = pygame.Rect(WINDOW_WIDTH-250, 50, health_width, health_height)
        
        # Draw health bar backgrounds
        pygame.draw.rect(surface, self.colors['gray'], p1_health_bg)
        pygame.draw.rect(surface, self.colors['gray'], p2_health_bg)
        
        # Draw actual health bars
        pygame.draw.rect(surface, self.colors['green'], p1_health_rect)
        pygame.draw.rect(surface, self.colors['green'], p2_health_rect)

        # Draw health text
        health_text1 = self.font.render(f"{int(self.player1_health)}/{self.player1_max_health}", True, self.colors['black'])
        health_text2 = self.font.render(f"{int(self.player2_health)}/{self.player2_max_health}", True, self.colors['black'])
        
        surface.blit(health_text1, (50, 75))
        surface.blit(health_text2, (WINDOW_WIDTH-250, 75))