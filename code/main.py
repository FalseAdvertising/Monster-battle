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
            
        player_choice, ai_choice = result
        print(f"Player selected: {player_choice}")
        print(f"AI selected: {ai_choice}")
        
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
            self.player_monster = Monster(player_choice, (200, 470), is_player=True)
            self.enemy_monster = Monster(ai_choice, (1000, 200), is_player=False)
            
            # Add to sprite groups
            self.monster_group.add(self.player_monster, self.enemy_monster)
            self.all_sprites.add(self.monster_group)
            
            # Create battle engine
            self.battle_engine = BattleEngine(self.player_monster, self.enemy_monster)
            
            # Create UI
            self.battle_ui = BattleUI(self.player_monster, self.enemy_monster)
            print("Game elements created successfully")
        except Exception as e:
            print(f"Error creating game elements: {e}")
            self.running = False

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]  # Left click

        # Check for button clicks
        selected_action = self.battle_ui.handle_input(mouse_pos, mouse_click)
        
        if selected_action:  # Only process if an action was selected
            if selected_action == 'end_game':
                self.running = False
            else:  # It's an ability
                print(f"\nNew turn starting - {selected_action} selected")
                winner = self.battle_engine.run_turn(selected_action)
                
                self.battle_ui.update_health_display(
                    self.player_monster.health,
                    self.enemy_monster.health
                )
                
                if winner:
                    print(f"Battle ended! Winner: {winner.name}")

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