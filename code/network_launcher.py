import pygame
import subprocess
import sys
import socket
import threading
from settings import *

class NetworkLauncher:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle - Network Launcher')
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Font setup
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        # Button setup
        self.buttons = self.setup_buttons()
        
        # Server process
        self.server_process = None
        self.server_running = False
        
    def setup_buttons(self):
        """Setup UI buttons"""
        button_width = 300
        button_height = 80
        spacing = 30
        
        center_x = WINDOW_WIDTH // 2
        start_y = WINDOW_HEIGHT // 2 - 100
        
        return [
            {
                'rect': pygame.Rect(center_x - button_width // 2, start_y, button_width, button_height),
                'text': 'Host Game (Server)',
                'action': 'host',
                'color': (0, 150, 0),
                'hover': False
            },
            {
                'rect': pygame.Rect(center_x - button_width // 2, start_y + button_height + spacing, button_width, button_height),
                'text': 'Join Game (Client)',
                'action': 'join',
                'color': (0, 0, 150),
                'hover': False
            },
            {
                'rect': pygame.Rect(center_x - button_width // 2, start_y + 2 * (button_height + spacing), button_width, button_height),
                'text': 'Local Game',
                'action': 'local',
                'color': (150, 150, 0),
                'hover': False
            }
        ]
        
    def get_local_ip(self):
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except:
            return "127.0.0.1"
            
    def start_server(self):
        """Start the game server"""
        try:
            self.server_process = subprocess.Popen([
                sys.executable, 
                'network_server.py'
            ], cwd='code')
            self.server_running = True
            return True
        except Exception as e:
            print(f"Failed to start server: {e}")
            return False
            
    def stop_server(self):
        """Stop the game server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            self.server_running = False
            
    def start_client(self, server_ip='localhost'):
        """Start the game client"""
        try:
            subprocess.Popen([
                sys.executable, 
                'network_game.py'
            ], cwd='code')
            return True
        except Exception as e:
            print(f"Failed to start client: {e}")
            return False
            
    def start_local_game(self):
        """Start local game"""
        try:
            subprocess.Popen([
                sys.executable, 
                'main.py'
            ], cwd='code')
            return True
        except Exception as e:
            print(f"Failed to start local game: {e}")
            return False
            
    def handle_input(self, mouse_pos, mouse_click):
        """Handle mouse input"""
        # Update hover states
        for button in self.buttons:
            button['hover'] = button['rect'].collidepoint(mouse_pos)
            
        # Handle clicks
        if mouse_click:
            for button in self.buttons:
                if button['rect'].collidepoint(mouse_pos):
                    return button['action']
        return None
        
    def draw(self):
        """Draw the launcher UI"""
        self.display_surface.fill((30, 30, 30))
        
        # Title
        title = self.font_large.render("Monster Battle", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.display_surface.blit(title, title_rect)
        
        subtitle = self.font_medium.render("Network Launcher", True, (200, 200, 200))
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.display_surface.blit(subtitle, subtitle_rect)
        
        # Buttons
        for button in self.buttons:
            color = button['color']
            if button['hover']:
                color = tuple(min(255, c + 50) for c in color)
                
            pygame.draw.rect(self.display_surface, color, button['rect'], border_radius=10)
            pygame.draw.rect(self.display_surface, (255, 255, 255), button['rect'], 3, border_radius=10)
            
            text = self.font_small.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            self.display_surface.blit(text, text_rect)
            
        # Instructions
        instructions = [
            "Host Game: Start a server and wait for players",
            "Join Game: Connect to an existing server",
            "Local Game: Play on the same computer"
        ]
        
        y_offset = WINDOW_HEIGHT - 150
        for instruction in instructions:
            text = self.font_small.render(instruction, True, (150, 150, 150))
            self.display_surface.blit(text, (50, y_offset))
            y_offset += 30
            
        # Server status
        if self.server_running:
            local_ip = self.get_local_ip()
            status_text = f"Server running on {local_ip}:12345"
            text = self.font_small.render(status_text, True, (0, 255, 0))
            self.display_surface.blit(text, (50, 50))
            
        pygame.display.update()
        
    def run(self):
        """Run the launcher"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = False
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_click = True
                    
            action = self.handle_input(mouse_pos, mouse_click)
            
            if action == 'host':
                if not self.server_running:
                    print("Starting server...")
                    if self.start_server():
                        local_ip = self.get_local_ip()
                        print(f"Server started on {local_ip}:12345")
                        print("Other players can connect using this IP address")
                        
                        # Wait a moment for server to start
                        pygame.time.wait(2000)
                        
                        # Start client for host
                        print("Starting client for host...")
                        self.start_client()
                    else:
                        print("Failed to start server!")
                        
            elif action == 'join':
                # For now, just start client (it will prompt for IP)
                print("Starting client...")
                self.start_client()
                
            elif action == 'local':
                print("Starting local game...")
                self.start_local_game()
                self.running = False
                
            self.draw()
            self.clock.tick(60)
            
        # Cleanup
        self.stop_server()
        pygame.quit()

if __name__ == '__main__':
    launcher = NetworkLauncher()
    launcher.run()