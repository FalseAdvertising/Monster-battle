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
    def __init__(self, player1_monster, player2_monster, battle_ui):
        self.player1_monster = player1_monster
        self.player2_monster = player2_monster
        self.player1_first = True  # Tracks who goes first
        self.ui = battle_ui
        # Track move confirmations and selected moves
        self.player1_confirmed = False
        self.player2_confirmed = False
        self.player1_selected_move = None
        self.player2_selected_move = None

    def confirm_move(self, player_number, move):
        """Confirm a move for a specific player"""
        if player_number == 1:
            self.player1_selected_move = move
            self.player1_confirmed = True
        else:
            self.player2_selected_move = move
            self.player2_confirmed = True
        
    def are_moves_confirmed(self):
        """Check if both players have confirmed their moves"""
        return self.player1_confirmed and self.player2_confirmed
    
    def reset_confirmations(self):
        """Reset confirmation status for a new turn"""
        self.player1_confirmed = False
        self.player2_confirmed = False
        self.player1_selected_move = None
        self.player2_selected_move = None

    def run_turn(self, player1_move=None, player2_move=None):
        """Execute a turn with both players' moves"""
        if player1_move is not None:
            self.confirm_move(1, player1_move)
        if player2_move is not None:
            self.confirm_move(2, player2_move)
            
        # Only proceed if both players have confirmed their moves
        if not self.are_moves_confirmed():
            return None
            
        first_monster = self.player1_monster if self.player1_first else self.player2_monster
        second_monster = self.player2_monster if self.player1_first else self.player1_monster
        first_move = self.player1_selected_move if self.player1_first else self.player2_selected_move
        second_move = self.player2_selected_move if self.player1_first else self.player1_selected_move

        # First player's move
        if first_move:
            damage = self.calculate_damage(first_monster, second_monster, first_move)
            second_monster.health -= damage
            # Trigger attack animation before showing damage
            self.ui.play_attack_animation(self.player1_first, first_move)
            print(f"{first_monster.name} used {first_move} for {damage:.1f} damage!")
            
            if second_monster.health <= 0:
                self.reset_confirmations()
                return first_monster

        # Second player's move
        if second_move and second_monster.health > 0:
            damage = self.calculate_damage(second_monster, first_monster, second_move)
            first_monster.health -= damage
            # Trigger attack animation before showing damage
            self.ui.play_attack_animation(not self.player1_first, second_move)
            print(f"{second_monster.name} used {second_move} for {damage:.1f} damage!")
            
            if first_monster.health <= 0:
                self.reset_confirmations()
                return second_monster

        # Alternate who goes first next turn and reset confirmations for the next turn
        self.player1_first = not self.player1_first
        self.reset_confirmations()
        return None

    def calculate_damage(self, attacker, defender, ability_name):
        """Calculate damage based on ability and types"""
        try:
            # Debug prints to verify data
            print(f"Attacker: {attacker.name}, Defender: {defender.name}")
            print(f"Ability: {ability_name}")
            print(f"Attacker stats: {MONSTER_DATA[attacker.name]}")
            
            # Get base damage
            base_damage = ABILITIES_DATA[ability_name]['damage']
            
            # Get type effectiveness
            type_multiplier = ELEMENT_DATA[attacker.element][defender.element]
            
            # Get attack and defense stats
            attack_stat = MONSTER_DATA[attacker.name]['attack']
            defense_stat = MONSTER_DATA[defender.name]['defense']
            
            # Calculate damage with stat modifier
            stat_multiplier = attack_stat / defense_stat
            final_damage = base_damage * type_multiplier * stat_multiplier
            
            print(f"Damage calculation: {base_damage} * {type_multiplier} * ({attack_stat}/{defense_stat})")
            
            return final_damage

        except KeyError as e:
            print(f"Error accessing stats: {e}")
            print(f"Available monster data: {list(MONSTER_DATA.keys())}")
            return 10
        except Exception as e:
            print(f"Unexpected error: {e}")
            return 10