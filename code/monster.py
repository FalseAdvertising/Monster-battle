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
        
        # Status effects
        self.shield_active = False
        self.burn_turns = 0
        
        # Special move tracking
        self.special_used = False
        
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
            self.abilities.append('burning_fury')  # Special move
            print(f"Added fire abilities: {self.abilities}")
        elif self.element == 'water':
            self.abilities.append('shards')
            self.abilities.append('splash')
            self.abilities.append('healing_wave')  # Special move
            print(f"Added water abilities: {self.abilities}")
        elif self.element == 'plant':
            self.abilities.append('spiral')
            self.abilities.append('earthquake')
            self.abilities.append('reflect_shield')  # Special move
            print(f"Added plant abilities: {self.abilities}")
            
    def get_available_abilities(self):
        """Get list of currently available abilities (excludes used special moves)"""
        available = []
        for ability in self.abilities:
            if ability in ABILITIES_DATA and ABILITIES_DATA[ability].get('type') == 'special':
                if not self.special_used:
                    available.append(ability)
            else:
                available.append(ability)
        return available
            
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
        # Check if shield is active (reflects damage)
        if self.shield_active and amount > 0:
            print(f"{self.name}'s shield reflects {amount} damage!")
            self.shield_active = False  # Shield is consumed after one use
            return amount  # Return damage to be reflected to attacker
        
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            return True  # Monster fainted
        return False
    
    def heal(self, amount):
        """Heal the monster"""
        old_health = self.health
        self.health = min(self.max_health, self.health + amount)
        healed = self.health - old_health
        print(f"{self.name} healed for {healed} HP!")
        return healed
    
    def apply_burn(self):
        """Apply burn damage at start of turn"""
        if self.burn_turns > 0:
            burn_damage = max(1, self.max_health // 10)  # 10% of max health as burn damage
            self.health -= burn_damage
            self.burn_turns -= 1
            print(f"{self.name} takes {burn_damage} burn damage! ({self.burn_turns} turns remaining)")
            if self.health <= 0:
                self.health = 0
                return True  # Monster fainted from burn
        return False
    
    def activate_special_move(self, move_name):
        """Activate a special move and mark it as used"""
        if move_name in ABILITIES_DATA and ABILITIES_DATA[move_name].get('type') == 'special':
            if not self.special_used:
                self.special_used = True
                print(f"{self.name} uses their special move: {move_name}!")
                return True
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