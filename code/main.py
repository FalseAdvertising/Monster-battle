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
                player_num = "1" if winner == self.player1_monster else "2"
                print(f"Battle ended! Player {player_num} wins!")

    def update(self):
        self.all_sprites.update()

    def draw(self):
        # Draw UI (includes background, floors, and UI elements)
        self.battle_ui.draw(self.display_surface)
        
        # Draw sprites
        self.all_sprites.draw(self.display_surface)
        
        pygame.display.update()

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