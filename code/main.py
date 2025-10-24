import pygame
from settings import *
from support import *
from timer import Timer
from monster import Monster
from ui import * 
from battle_engine import BattleEngine

class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Monster Battle')
        self.clock = pygame.time.Clock()
        self.running = True

        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.monster_group = pygame.sprite.Group()

        # Create monsters with correct is_player values
        self.player_monster = Monster('Plumette', (200, 470), is_player=True)   # Shows back sprite
        self.enemy_monster = Monster('Sparchu', (1000, 200), is_player=False)   # Shows front sprite
        
        # Add to sprite groups
        self.monster_group.add(self.player_monster, self.enemy_monster)
        self.all_sprites.add(self.monster_group)
        
        # Create battle engine
        self.battle_engine = BattleEngine(self.player_monster, self.enemy_monster)
        
        # Create UI
        self.battle_ui = BattleUI(self.player_monster, self.enemy_monster)
        print("Game elements created successfully")

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]  # Left click

        # Check for button clicks
        selected_action = self.battle_ui.handle_input(mouse_pos, mouse_click)
        
        if selected_action == 'end_game':
            self.running = False
        elif selected_action:  # It's an ability
            # Run battle turn and get winner (if any)
            winner = self.battle_engine.run_turn(selected_action)
            
            # Update UI with new health values
            self.battle_ui.update_health_display(
                self.player_monster.health,
                self.enemy_monster.health
            )
            
            # Check for battle end but don't close window
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