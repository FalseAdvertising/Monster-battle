import pygame
from settings import *
from support import *

class Monster(pygame.sprite.Sprite):
    def __init__(self, name, position, is_player=True):
        super().__init__()
        
        # Basic attributes
        self.name = name
        self.stats = MONSTER_DATA[name]
        self.is_player = is_player
        
        # Stats from settings
        self.health = self.stats['health']
        self.max_health = self.stats['health']
        self.element = self.stats['element']
        
        # Set up abilities
        self.abilities = ['scratch']  # Basic ability for all monsters
        self.add_element_abilities()
        
        # Load images and set correct sprite
        self.load_images()
        # Changed logic here - player sees back sprite, enemy shows front sprite
        self.image = self.back_sprite if is_player else self.front_sprite
        self.rect = self.image.get_rect(center=position)

    def add_element_abilities(self):
        """Add element-specific abilities based on monster's element"""
        print(f"Adding abilities for {self.name} with element {self.element}")
        
        if self.element == 'fire':
            self.abilities.append('nuke')
            self.abilities.append('spark')
            print(f"Added fire abilities: {self.abilities}")
        elif self.element == 'water':
            self.abilities.append('shards')
            self.abilities.append('spark')
            print(f"Added water abilities: {self.abilities}")
        elif self.element == 'plant':
            self.abilities.extend(['spiral'])
            print(f"Added plant abilities: {self.abilities}")
            
    def load_images(self):
        """Load all sprite variations for the monster"""
        # Load from respective folders
        front_sprites = folder_importer('images', 'front')
        back_sprites = folder_importer('images', 'back')
        simple_sprites = folder_importer('images', 'simple')
        
        try:
            self.front_sprite = front_sprites[self.name]
            self.back_sprite = back_sprites[self.name]
            self.simple_sprite = simple_sprites[self.name]
        except KeyError as e:
            print(f"Failed to load sprite for {self.name}: {e}")
            
    def take_damage(self, amount):
        """Handle damage taken by monster"""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True  # Monster fainted
        return False
        
    def use_ability(self, ability_name, target):
        """Use an ability on a target monster"""
        if ability_name not in self.abilities:
            return False
            
        ability_data = ABILITIES_DATA[ability_name]
        base_damage = ability_data['damage']
        
        # Calculate type effectiveness
        multiplier = ELEMENT_DATA[self.element][target.element]
        final_damage = base_damage * multiplier
        
        return target.take_damage(final_damage)
        
    def update(self):
        """Update monster state each frame"""
        # Add animation or state updates here
        pass