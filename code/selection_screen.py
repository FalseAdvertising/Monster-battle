import pygame
import random
from settings import *

class MonsterCard:
    def __init__(self, name, position):
        self.name = name
        self.stats = MONSTER_DATA[name]
        
        # Load simple sprite
        self.image = pygame.image.load(f'images/simple/{name.lower()}.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        
        # Card dimensions
        self.card_width = 200
        self.card_height = 250
        self.card_rect = pygame.Rect(position[0], position[1], self.card_width, self.card_height)
        
        # Colors
        self.normal_color = COLORS['gray']
        self.hover_color = COLORS['light_gray']
        self.current_color = self.normal_color
        
        # Font
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, surface):
        # Draw card background
        pygame.draw.rect(surface, self.current_color, self.card_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['dark_gray'], self.card_rect, 3, border_radius=10)
        
        # Draw monster sprite
        sprite_rect = self.image.get_rect(
            center=(self.card_rect.centerx, self.card_rect.top + 80)
        )
        surface.blit(self.image, sprite_rect)
        
        # Draw monster name
        name_text = self.font.render(self.name, True, COLORS['black'])
        name_rect = name_text.get_rect(
            center=(self.card_rect.centerx, self.card_rect.top + 160)
        )
        surface.blit(name_text, name_rect)
        
        # Draw stats
        y_offset = 180
        stats_to_show = ['element', 'health', 'attack', 'defense']
        for stat in stats_to_show:
            stat_text = self.font.render(f"{stat}: {self.stats[stat]}", True, COLORS['black'])
            stat_rect = stat_text.get_rect(
                center=(self.card_rect.centerx, self.card_rect.top + y_offset)
            )
            surface.blit(stat_text, stat_rect)
            y_offset += 20

    def handle_hover(self, mouse_pos):
        if self.card_rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.normal_color
        return False

class SelectionScreen:
    def __init__(self):
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create monster cards
        self.cards = []
        self.setup_cards()
        
    def setup_cards(self):
        # Get all monster names and randomly select 8
        all_monsters = list(MONSTER_DATA.keys())
        selected_monsters = random.sample(all_monsters, 8)
        
        # Setup grid layout for the 8 selected monsters
        cards_per_row = 4
        x_spacing = WINDOW_WIDTH // (cards_per_row + 1)
        y_spacing = 300
        
        for i, name in enumerate(selected_monsters):
            row = i // cards_per_row
            col = i % cards_per_row
            pos = (x_spacing * (col + 1) - 100, 150 + row * y_spacing)
            self.cards.append(MonsterCard(name, pos))
            print(f"Added card for: {name}")  # Debug print

    def run(self):
        while self.running:
            self.display_surface.fill(COLORS['white'])
            
            # Draw title
            font = pygame.font.Font(None, 74)
            text = font.render("Select Your Monster", True, COLORS['black'])
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.display_surface.blit(text, text_rect)
            
            # Handle events
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                # Check specifically for left mouse button (button 1)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for card in self.cards:
                        if card.handle_hover(mouse_pos):
                            # Choose random opponent
                            opponents = [c.name for c in self.cards if c.name != card.name]
                            ai_choice = random.choice(opponents)
                            return (card.name, ai_choice)
            
            # Draw cards and handle hover effects
            for card in self.cards:
                card.handle_hover(mouse_pos)
                card.draw(self.display_surface)
            
            pygame.display.update()
            self.clock.tick(60)

        return None