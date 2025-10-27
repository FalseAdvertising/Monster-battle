import pygame
import random
import math
import os
from settings import *

class MonsterCard:
    def __init__(self, name, position):
        self.name = name
        self.stats = MONSTER_DATA[name]
        # Load simple sprite
        self.image = pygame.image.load(f'images/simple/{name.lower()}.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=position)
        # Card dimensions
        self.card_width = 220
        self.card_height = 270
        self.card_rect = pygame.Rect(position[0], position[1], self.card_width, self.card_height)
        # Wood texture for box background
        self.wood_texture = pygame.image.load('images/other/wood_sign.png').convert_alpha()
        # Colors
        self.normal_color = (120, 100, 80)  # fallback for logic, not drawn
        self.hover_color = (160, 130, 110)
        self.current_color = self.normal_color
        self.glow_color = (180, 0, 255)
        self.selected_glow_color = (255, 120, 0)
        # Spooky font (fallback to system if not found)
        spooky_font_path = os.path.join('background', 'Creepster-Regular.ttf')
        if os.path.exists(spooky_font_path):
            self.font = pygame.font.Font(spooky_font_path, 28)
            self.stats_font = pygame.font.Font(spooky_font_path, 22)
        else:
            self.font = pygame.font.SysFont('Chiller', 28) if 'chiller' in [f.lower() for f in pygame.font.get_fonts()] else pygame.font.SysFont('Comic Sans MS', 28)
            self.stats_font = pygame.font.SysFont('Chiller', 22) if 'chiller' in [f.lower() for f in pygame.font.get_fonts()] else pygame.font.SysFont('Comic Sans MS', 22)
        # Animation state
        self.anim_pulse = 0.0
        self.selected = False

    def draw(self, surface, animate=False):
        # Animate scale if hovered/selected
        scale = 1.0
        if animate or self.selected:
            self.anim_pulse += 0.18
            scale = 1.08 + 0.04 * math.sin(self.anim_pulse)
        else:
            self.anim_pulse = 0.0
        # Card background with wood texture
        card_rect = self.card_rect.copy()
        if scale != 1.0:
            card_rect = card_rect.inflate(int(card_rect.width * (scale - 1)), int(card_rect.height * (scale - 1)))
            card_rect.center = self.card_rect.center
        wood_bg = pygame.transform.smoothscale(self.wood_texture, (card_rect.width, card_rect.height))
        surface.blit(wood_bg, card_rect)
        # Glowing border
        border_color = self.selected_glow_color if self.selected else self.glow_color if animate else (80, 0, 80)
        pygame.draw.rect(surface, border_color, card_rect, 6, border_radius=18)
        # Monster sprite (larger, with shadow)
        sprite_size = 100 if animate or self.selected else 80
        sprite = pygame.transform.smoothscale(self.image, (sprite_size, sprite_size))
        sprite_rect = sprite.get_rect(center=(card_rect.centerx, card_rect.top + 75))
        shadow = pygame.Surface((sprite_size, sprite_size), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,80), shadow.get_rect())
        surface.blit(shadow, (sprite_rect.x+4, sprite_rect.y+8))
        surface.blit(sprite, sprite_rect)
        # Monster name
        name_text = self.font.render(self.name, True, COLORS['white'])
        name_rect = name_text.get_rect(center=(card_rect.centerx, card_rect.top + 145))
        surface.blit(name_text, name_rect)
        # Stats (left-aligned, larger font, padding)
        y_offset = card_rect.top + 170
        x_offset = card_rect.left + 24
        stats_to_show = ['element', 'health', 'attack', 'defense']
        for stat in stats_to_show:
            stat_text = self.stats_font.render(f"{stat}: {self.stats[stat]}", True, COLORS['white'])
            stat_rect = stat_text.get_rect(topleft=(x_offset, y_offset))
            surface.blit(stat_text, stat_rect)
            y_offset += 28

    def handle_hover(self, mouse_pos):
        if self.card_rect.collidepoint(mouse_pos):
            self.current_color = self.hover_color
            return True
        self.current_color = self.normal_color
        return False
    def set_selected(self, selected):
        self.selected = selected

class SelectionScreen:
    def __init__(self):
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.current_player = 1
        self.player1_choice = None
        self.cards = []
        self.setup_cards()
        # Animated background
        bg_path = os.path.normpath(os.path.join('background', 'Player-Select-BG.jpg'))
        try:
            self.bg_img = pygame.image.load(bg_path).convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (WINDOW_WIDTH + 80, WINDOW_HEIGHT + 40))
        except Exception as e:
            print(f"Could not load selection background: {bg_path}: {e}")
            self.bg_img = None
        self.bg_anim_offset = 0.0
        self.bg_anim_dir = 1

    def setup_cards(self):
        all_monsters = list(MONSTER_DATA.keys())
        selected_monsters = random.sample(all_monsters, 8)
        cards_per_row = 4
        x_spacing = WINDOW_WIDTH // (cards_per_row + 1)
        y_spacing = 300
        for i, name in enumerate(selected_monsters):
            row = i // cards_per_row
            col = i % cards_per_row
            pos = (x_spacing * (col + 1) - 100, 150 + row * y_spacing)
            self.cards.append(MonsterCard(name, pos))

    def run(self):
        while self.running:
            # Animated background
            if self.bg_img:
                self.bg_anim_offset += self.bg_anim_dir * 0.15
                if abs(self.bg_anim_offset) > 40:
                    self.bg_anim_dir *= -1
                scale = 1.01 + 0.01 * math.sin(pygame.time.get_ticks() / 800.0)
                bg_scaled = pygame.transform.smoothscale(self.bg_img, (int(self.bg_img.get_width() * scale), int(self.bg_img.get_height() * scale)))
                x = int(-40 + self.bg_anim_offset)
                y = int(-20 + 10 * math.sin(pygame.time.get_ticks() / 1200.0))
                self.display_surface.blit(bg_scaled, (x, y))
            else:
                self.display_surface.fill(COLORS['white'])

            # Draw title
            # Spooky title font
            spooky_font_path = os.path.join('background', 'Creepster-Regular.ttf')
            if os.path.exists(spooky_font_path):
                title_font = pygame.font.Font(spooky_font_path, 80)
            else:
                title_font = pygame.font.SysFont('Chiller', 80) if 'chiller' in [f.lower() for f in pygame.font.get_fonts()] else pygame.font.SysFont('Comic Sans MS', 80)
            text = title_font.render(f"Player {self.current_player} Select Your Monster", True, (255, 80, 40))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.display_surface.blit(text, text_rect)

            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None, None
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for card in self.cards:
                        if card.handle_hover(mouse_pos):
                            if self.current_player == 1:
                                self.player1_choice = card.name
                                self.current_player = 2
                                self.cards = [c for c in self.cards if c.name != card.name]
                                break
                            else:
                                return self.player1_choice, card.name

            # Draw cards and handle hover effects
            for idx, card in enumerate(self.cards):
                hovered = card.handle_hover(mouse_pos)
                card.set_selected(False)
                card.draw(self.display_surface, animate=hovered)

            pygame.display.update()
            self.clock.tick(60)
        return None, None