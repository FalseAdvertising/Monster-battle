import random
from settings import *

class Move:
    def __init__(self, name, damage, element):
        self.name = name
        self.damage = damage
        self.element = element

class AIController:
    def choose_move(self, monster):
        return random.choice(monster.abilities)

class BattleEngine:
    def __init__(self, player_monster, enemy_monster):
        self.player_monster = player_monster
        self.enemy_monster = enemy_monster
        self.ai_controller = AIController()

    def run_turn(self, player_ability):
        """Execute a turn using the selected player ability"""
        # Player's turn
        if player_ability:
            damage = self.calculate_damage(self.player_monster, self.enemy_monster, player_ability)
            self.enemy_monster.health -= damage
            print(f"{self.player_monster.name} used {player_ability} for {damage:.1f} damage!")
            
            if self.enemy_monster.health <= 0:
                print(f"{self.enemy_monster.name} fainted!")
                return self.player_monster

        # Enemy's turn
        enemy_ability = self.ai_controller.choose_move(self.enemy_monster)
        damage = self.calculate_damage(self.enemy_monster, self.player_monster, enemy_ability)
        self.player_monster.health -= damage
        print(f"{self.enemy_monster.name} used {enemy_ability} for {damage:.1f} damage!")

        if self.player_monster.health <= 0:
            print(f"{self.player_monster.name} fainted!")
            return self.enemy_monster

        return None

    def calculate_damage(self, attacker, defender, ability_name):
        """Calculate damage based on ability and types"""
        base_damage = ABILITIES_DATA[ability_name]['damage']
        type_multiplier = ELEMENT_DATA[attacker.element][defender.element]
        return base_damage * type_multiplier