import pygame
import sys
import socket
from settings import *
from network_client import NetworkClient
from selection_screen import SelectionScreen

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
        pygame.display.set_caption('Monster Battle - Connecting...')
        self.clock = pygame.time.Clock()
        
        # Connect to server
        self.client = NetworkClient(server_ip)
        self.running = True
        self.battle_ui = None
        
        # Show connecting screen while attempting connection
        self.show_connecting_screen()
        
        if not self.client.connect():
            print("Failed to connect to server!")
            self.show_connection_failed()
            return
            
        print("Connected successfully! Starting game interface...")
        
    def show_connecting_screen(self):
        """Show connecting screen"""
        self.display_surface.fill((0, 0, 50))
        font = pygame.font.Font(None, 48)
        text = font.render("Connecting to server...", True, (255, 255, 255))
        text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.display_surface.blit(text, text_rect)
        
        small_font = pygame.font.Font(None, 24)
        tip = small_font.render(f"Connecting to {self.client.host}:{self.client.port}", True, (200, 200, 200))
        tip_rect = tip.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
        self.display_surface.blit(tip, tip_rect)
        
        pygame.display.update()
        
    def show_connection_failed(self):
        """Show connection failed screen"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                    pygame.quit()
                    return
                    
            self.display_surface.fill((50, 0, 0))
            font = pygame.font.Font(None, 48)
            text = font.render("Connection Failed", True, (255, 100, 100))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.display_surface.blit(text, text_rect)
            
            small_font = pygame.font.Font(None, 24)
            tip = small_font.render("Press any key to exit", True, (200, 200, 200))
            tip_rect = tip.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.display_surface.blit(tip, tip_rect)
            
            error_text = small_font.render("Make sure the server is running!", True, (255, 200, 200))
            error_rect = error_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.display_surface.blit(error_text, error_rect)
            
            pygame.display.update()
            self.clock.tick(60)
        
    def run(self):
        """Run the network game"""
        # Check if connection was successful
        if not self.client.connected:
            print("Connection failed - exiting")
            pygame.quit()
            return
            
        print("Waiting for player assignment...")
        pygame.display.set_caption('Monster Battle - Waiting for Assignment...')
        
        # Wait for player ID with visual feedback and connection monitoring
        assignment_timeout = 0
        max_assignment_wait = 300  # 5 seconds at 60 FPS
        
        while self.running and self.client.player_id is None and self.client.connected:
            self.client.process_messages()
            
            # Check for assignment timeout
            assignment_timeout += 1
            if assignment_timeout > max_assignment_wait:
                print("Timeout waiting for player assignment")
                break
            
            self.display_surface.fill((0, 0, 100))
            font = pygame.font.Font(None, 48)
            text = font.render("Waiting for player assignment...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.display_surface.blit(text, text_rect)
            
            # Show connection status
            small_font = pygame.font.Font(None, 24)
            status = "Connected to server" if self.client.connected else "Connection lost"
            color = (0, 255, 0) if self.client.connected else (255, 0, 0)
            status_text = small_font.render(status, True, color)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            self.display_surface.blit(status_text, status_rect)
            
            # Show timeout countdown
            remaining = (max_assignment_wait - assignment_timeout) // 60
            if remaining > 0:
                timeout_text = small_font.render(f"Timeout in: {remaining}s", True, (255, 255, 0))
                timeout_rect = timeout_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 80))
                self.display_surface.blit(timeout_text, timeout_rect)
            
            pygame.display.update()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    
            self.clock.tick(60)
            
        if not self.client.connected:
            print("Lost connection to server")
            self.show_error("Lost connection to server")
            return
            
        if self.client.player_id is None:
            print("Failed to get player assignment")
            self.show_error("Server assignment timeout")
            return
            
        if not self.running:
            self.client.disconnect()
            pygame.quit()
            return
            
        pygame.display.set_caption(f'Monster Battle - Player {self.client.player_id}')
        print(f"Successfully assigned as Player {self.client.player_id}")
        
        # Wait for game start with visual feedback
        game_start_timeout = 0
        max_game_wait = 1800  # 30 seconds at 60 FPS
        
        while self.running and self.client.game_state == 'waiting' and self.client.connected:
            self.client.process_messages()
            
            game_start_timeout += 1
            if game_start_timeout > max_game_wait:
                print("Timeout waiting for game to start")
                break
            
            self.display_surface.fill((0, 50, 0))
            font = pygame.font.Font(None, 48)
            text = font.render("Waiting for other player...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.display_surface.blit(text, text_rect)
            
            # Show player info
            small_font = pygame.font.Font(None, 32)
            player_text = f"You are Player {self.client.player_id}"
            player_surface = small_font.render(player_text, True, (200, 255, 200))
            player_rect = player_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.display_surface.blit(player_surface, player_rect)
            
            # Show connection status
            status = "Connected" if self.client.connected else "Disconnected"
            color = (0, 255, 0) if self.client.connected else (255, 0, 0)
            status_text = small_font.render(f"Status: {status}", True, color)
            status_rect = status_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            self.display_surface.blit(status_text, status_rect)
            
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
    """Get server IP from user with better prompts"""
    print("=== Monster Battle Network Client ===")
    print()
    print("IMPORTANT: Make sure the server is running first!")
    print("You can start the server by:")
    print("1. Running 'python network_server.py' in another terminal")
    print("2. Or using the Network Launcher and clicking 'Host Game'")
    print()
    print("Enter server IP address:")
    print("- Press Enter for localhost (127.0.0.1)")
    print("- Or enter the host's IP address (e.g., 192.168.1.100)")
    print()
    
    while True:
        try:
            server_ip = input("Server IP: ").strip()
            
            if not server_ip:
                server_ip = 'localhost'
                
            print(f"Will attempt to connect to: {server_ip}:12345")
            confirm = input("Is this correct? (y/n): ").strip().lower()
            
            if confirm in ['y', 'yes', '']:
                return server_ip
            elif confirm in ['n', 'no']:
                continue
            else:
                continue
                
        except KeyboardInterrupt:
            print("\nCancelled by user")
            return None

def check_server_running(host, port):
    """Check if server is running before connecting"""
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.settimeout(3)
        result = test_socket.connect_ex((host, port))
        test_socket.close()
        return result == 0
    except:
        return False

if __name__ == '__main__':
    server_ip = get_server_ip()
    
    if server_ip is None:
        sys.exit(0)
        
    # Check if server is running before starting the game
    print(f"\nChecking if server is running at {server_ip}:12345...")
    
    if not check_server_running(server_ip, 12345):
        print(f"❌ No server found at {server_ip}:12345")
        print("\nTo fix this:")
        print("1. Make sure the server is running first")
        print("2. Check the IP address is correct")
        print("3. Make sure you're on the same network")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
        
    print(f"✅ Server found! Starting game...")
    
    game = NetworkGame(server_ip)
    game.run()