import pygame
import sys
from settings import *
from network_client import NetworkClient
from selection_screen import SelectionScreen
import socket

class NetworkSelectionScreen:
    def __init__(self, client):
        self.client = client
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(f'Monster Battle - Player {client.player_id}')
        self.clock = pygame.time.Clock()
        self.running = True
        self.monster_selected = False
        
        # Create monster cards (same as original selection screen)
        self.cards = []
        self.setup_cards()
        
    def setup_cards(self):
        """Setup monster selection cards"""
        # Import MonsterCard from selection_screen
        from selection_screen import MonsterCard
        
        all_monsters = list(MONSTER_DATA.keys())
        cards_per_row = 4
        x_spacing = WINDOW_WIDTH // (cards_per_row + 1)
        y_spacing = 300
        
        for i, name in enumerate(all_monsters[:8]):  # Show first 8 monsters
            row = i // cards_per_row
            col = i % cards_per_row
            pos = (x_spacing * (col + 1) - 100, 150 + row * y_spacing)
            self.cards.append(MonsterCard(name, pos))
            
    def run(self):
        """Run the network selection screen"""
        while self.running and self.client.connected:
            # Process network messages
            self.client.process_messages()
            
            # Check if we should proceed to battle
            if self.client.game_state == 'battle':
                return self.client.my_monster
                
            self.display_surface.fill(COLORS['white'])
            
            # Draw title
            font = pygame.font.Font(None, 80)
            title = f"Player {self.client.player_id} - Select Your Monster"
            if self.monster_selected:
                title = f"Player {self.client.player_id} - Waiting for opponent..."
                
            text = font.render(title, True, (255, 80, 40))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.display_surface.blit(text, text_rect)
            
            # Handle events
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.monster_selected:
                    for card in self.cards:
                        if card.handle_hover(mouse_pos):
                            self.client.send_monster_selection(card.name)
                            self.monster_selected = True
                            print(f"Selected {card.name}")
                            break
                            
            # Draw cards
            for card in self.cards:
                hovered = card.handle_hover(mouse_pos) and not self.monster_selected
                card.draw(self.display_surface, animate=hovered)
                
            pygame.display.update()
            self.clock.tick(60)
            
        return None

class NetworkBattleUI:
    def __init__(self, client):
        self.client = client
        self.display_surface = pygame.display.get_surface()
        
        # Load sprites
        self.load_monster_sprites()
        
        # UI colors
        self.colors = COLORS
        
        # Button setup
        self.buttons = []
        self.selected_move = None
        
        # Load fonts
        try:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except:
            self.font = pygame.font.SysFont(None, 36)
            self.small_font = pygame.font.SysFont(None, 24)
            
        self.setup_move_buttons()
        
    def load_monster_sprites(self):
        """Load monster sprites"""
        self.my_sprite = None
        self.opponent_sprite = None
        
        try:
            if self.client.my_monster:
                self.my_sprite = pygame.image.load(f'images/back/{self.client.my_monster}.png').convert_alpha()
                self.my_sprite = pygame.transform.scale(self.my_sprite, (200, 200))
                
            if self.client.opponent_monster:
                self.opponent_sprite = pygame.image.load(f'images/front/{self.client.opponent_monster}.png').convert_alpha()
                self.opponent_sprite = pygame.transform.scale(self.opponent_sprite, (200, 200))
        except Exception as e:
            print(f"Error loading sprites: {e}")
            
    def setup_move_buttons(self):
        """Setup move selection buttons"""
        self.buttons = []
        available_moves = self.client.get_available_moves()
        
        button_width = 200
        button_height = 50
        spacing = 20
        start_y = WINDOW_HEIGHT - 200
        
        for i, move in enumerate(available_moves[:4]):
            x = 50 + (i % 2) * (button_width + spacing)
            y = start_y + (i // 2) * (button_height + spacing)
            
            # Check if this is a special move
            is_special = move in ABILITIES_DATA and ABILITIES_DATA[move].get('type') == 'special'
            
            self.buttons.append({
                'rect': pygame.Rect(x, y, button_width, button_height),
                'move': move,
                'is_special': is_special,
                'hover': False
            })
            
    def handle_input(self, mouse_pos, mouse_click):
        """Handle mouse input"""
        if not self.client.waiting_for_move:
            return
            
        # Update hover states
        for button in self.buttons:
            button['hover'] = button['rect'].collidepoint(mouse_pos)
            
        # Handle clicks
        if mouse_click:
            for button in self.buttons:
                if button['rect'].collidepoint(mouse_pos):
                    self.client.send_move_selection(button['move'])
                    self.selected_move = button['move']
                    break
                    
    def draw(self):
        """Draw the battle UI"""
        self.display_surface.fill((50, 100, 50))  # Dark green background
        
        # Draw monsters
        if self.my_sprite:
            self.display_surface.blit(self.my_sprite, (100, 400))
        if self.opponent_sprite:
            self.display_surface.blit(self.opponent_sprite, (900, 200))
            
        # Draw health bars
        self.draw_health_bars()
        
        # Draw status effects
        self.draw_status_effects()
        
        # Draw move buttons
        self.draw_move_buttons()
        
        # Draw game info
        self.draw_game_info()
        
    def draw_health_bars(self):
        """Draw health bars for both players"""
        # My health bar
        my_health = self.client.get_my_health()
        my_max_health = self.client.get_my_max_health()
        
        if my_max_health > 0:
            health_ratio = my_health / my_max_health
            bar_width = 200
            bar_height = 20
            
            # Background
            pygame.draw.rect(self.display_surface, (100, 0, 0), (50, 50, bar_width, bar_height))
            # Health fill
            pygame.draw.rect(self.display_surface, (0, 255, 0), (50, 50, int(bar_width * health_ratio), bar_height))
            # Text
            text = self.small_font.render(f"You: {my_health}/{my_max_health}", True, (255, 255, 255))
            self.display_surface.blit(text, (50, 75))
            
        # Opponent health bar
        opp_health = self.client.get_opponent_health()
        opp_max_health = self.client.get_opponent_max_health()
        
        if opp_max_health > 0:
            health_ratio = opp_health / opp_max_health
            bar_width = 200
            bar_height = 20
            
            # Background
            pygame.draw.rect(self.display_surface, (100, 0, 0), (WINDOW_WIDTH - 250, 50, bar_width, bar_height))
            # Health fill
            pygame.draw.rect(self.display_surface, (255, 0, 0), (WINDOW_WIDTH - 250, 50, int(bar_width * health_ratio), bar_height))
            # Text
            text = self.small_font.render(f"Opponent: {opp_health}/{opp_max_health}", True, (255, 255, 255))
            self.display_surface.blit(text, (WINDOW_WIDTH - 250, 75))
            
    def draw_status_effects(self):
        """Draw status effect indicators"""
        my_status = self.client.get_my_status_effects()
        opp_status = self.client.get_opponent_status_effects()
        
        y_offset = 100
        
        # My status effects
        if my_status['shield_active']:
            text = self.small_font.render("🛡️ SHIELD", True, (0, 255, 255))
            self.display_surface.blit(text, (50, y_offset))
            y_offset += 25
            
        if my_status['burn_turns'] > 0:
            text = self.small_font.render(f"🔥 BURN ({my_status['burn_turns']})", True, (255, 100, 0))
            self.display_surface.blit(text, (50, y_offset))
            
        # Opponent status effects
        y_offset = 100
        if opp_status['shield_active']:
            text = self.small_font.render("🛡️ SHIELD", True, (0, 255, 255))
            self.display_surface.blit(text, (WINDOW_WIDTH - 250, y_offset))
            y_offset += 25
            
        if opp_status['burn_turns'] > 0:
            text = self.small_font.render(f"🔥 BURN ({opp_status['burn_turns']})", True, (255, 100, 0))
            self.display_surface.blit(text, (WINDOW_WIDTH - 250, y_offset))
            
    def draw_move_buttons(self):
        """Draw move selection buttons"""
        if not self.client.waiting_for_move:
            return
            
        for button in self.buttons:
            rect = button['rect']
            
            # Button background
            color = (100, 100, 255) if button['hover'] else (70, 70, 200)
            if button['is_special']:
                color = (255, 215, 0) if button['hover'] else (200, 170, 0)
                
            pygame.draw.rect(self.display_surface, color, rect, border_radius=5)
            pygame.draw.rect(self.display_surface, (255, 255, 255), rect, 2, border_radius=5)
            
            # Button text
            text_color = (0, 0, 0) if button['is_special'] else (255, 255, 255)
            text = self.small_font.render(button['move'], True, text_color)
            text_rect = text.get_rect(center=rect.center)
            self.display_surface.blit(text, text_rect)
            
    def draw_game_info(self):
        """Draw game information"""
        # Turn info
        text = self.font.render(f"Turn {self.client.turn}", True, (255, 255, 255))
        self.display_surface.blit(text, (WINDOW_WIDTH // 2 - 50, 50))
        
        # Player info
        player_text = f"You are Player {self.client.player_id}"
        text = self.small_font.render(player_text, True, (255, 255, 255))
        self.display_surface.blit(text, (WINDOW_WIDTH // 2 - 100, 100))
        
        # Waiting message
        if not self.client.waiting_for_move and self.client.game_state == 'battle':
            text = self.font.render("Waiting for opponent...", True, (255, 255, 0))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.display_surface.blit(text, text_rect)
            
        # Selected move
        if self.selected_move:
            text = self.small_font.render(f"Selected: {self.selected_move}", True, (0, 255, 0))
            self.display_surface.blit(text, (50, WINDOW_HEIGHT - 50))

class NetworkGame:
    def __init__(self, server_ip='localhost'):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle - Network')
        self.clock = pygame.time.Clock()
        
        # Connect to server
        self.client = NetworkClient(server_ip)
        if not self.client.connect():
            print("Failed to connect to server!")
            sys.exit(1)
            
        self.running = True
        self.battle_ui = None
        
    def run(self):
        """Run the network game"""
        print("Waiting for player assignment...")
        
        # Wait for player ID
        while self.running and self.client.player_id is None:
            self.client.process_messages()
            pygame.time.wait(100)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
        if not self.running:
            return
            
        pygame.display.set_caption(f'Monster Battle - Player {self.client.player_id}')
        print(f"You are Player {self.client.player_id}")
        
        # Wait for game start
        while self.running and self.client.game_state == 'waiting':
            self.client.process_messages()
            
            self.display_surface.fill((0, 0, 0))
            font = pygame.font.Font(None, 48)
            text = font.render("Waiting for other player...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.display_surface.blit(text, text_rect)
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            self.clock.tick(60)
            
        # Monster selection
        if self.running and self.client.game_state == 'selection':
            selection_screen = NetworkSelectionScreen(self.client)
            selected_monster = selection_screen.run()
            
            if not selected_monster:
                self.running = False
                return
                
        # Battle phase
        if self.running and self.client.game_state == 'battle':
            self.battle_ui = NetworkBattleUI(self.client)
            
            while self.running and self.client.game_state == 'battle':
                self.client.process_messages()
                
                # Handle events
                mouse_pos = pygame.mouse.get_pos()
                mouse_click = False
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_click = True
                        
                # Update UI
                if self.battle_ui:
                    self.battle_ui.handle_input(mouse_pos, mouse_click)
                    self.battle_ui.draw()
                    
                pygame.display.update()
                self.clock.tick(60)
                
        # Game finished
        if self.client.game_state == 'finished':
            self.show_results()
            
        self.client.disconnect()
        pygame.quit()
        
    def show_results(self):
        """Show battle results"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    self.running = False
                    
            self.display_surface.fill((0, 0, 0))
            
            font = pygame.font.Font(None, 72)
            
            # Determine if we won
            if self.client.players:
                my_health = self.client.get_my_health()
                opp_health = self.client.get_opponent_health()
                
                if my_health > 0:
                    text = font.render("YOU WIN!", True, (0, 255, 0))
                else:
                    text = font.render("YOU LOSE!", True, (255, 0, 0))
            else:
                text = font.render("Game Over", True, (255, 255, 255))
                
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.display_surface.blit(text, text_rect)
            
            # Instructions
            small_font = pygame.font.Font(None, 36)
            inst_text = small_font.render("Press any key to exit", True, (255, 255, 255))
            inst_rect = inst_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            self.display_surface.blit(inst_text, inst_rect)
            
            pygame.display.update()
            self.clock.tick(60)

def get_server_ip():
    """Get server IP from user"""
    # Simple console input for server IP
    print("=== Monster Battle Network ===")
    print("Enter server IP address (press Enter for localhost):")
    server_ip = input().strip()
    
    if not server_ip:
        server_ip = 'localhost'
        
    return server_ip

if __name__ == '__main__':
    server_ip = get_server_ip()
    game = NetworkGame(server_ip)
    game.run()