import random
import pygame
from settings import *
from animation import AttackAnimation, DamageFlash

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
        self.battle_ui = battle_ui
        self.turn_number = 1
        
        # Animation systems
        self.attack_animation = AttackAnimation()
        self.player1_flash = DamageFlash()
        self.player2_flash = DamageFlash()
        
        # Animation state
        self.animating = False
        self.animation_queue = []

    def run_turn(self, player1_move, player2_move):
        """Execute a turn with animations"""
        print(f"\n--- Turn {self.turn_number} ---")
        
        # Determine turn order (alternates each turn)
        if self.turn_number % 2 == 1:  # Odd turns: Player 1 goes first
            first_attacker, first_move = self.player1_monster, player1_move
            second_attacker, second_move = self.player2_monster, player2_move
        else:  # Even turns: Player 2 goes first
            first_attacker, first_move = self.player2_monster, player2_move
            second_attacker, second_move = self.player1_monster, player1_move

        # Queue animations
        self.animation_queue = [
            (first_attacker, first_move),
            (second_attacker, second_move)
        ]
        
        self.animating = True
        self.turn_number += 1
        
        return None  # Don't check winner until animations complete

    def update_animations(self, dt):
        """Update all animations"""
        self.attack_animation.update(dt)
        self.player1_flash.update(dt)
        self.player2_flash.update(dt)
        
        # Process animation queue
        if self.animating and not self.attack_animation.active and self.animation_queue:
            attacker, move = self.animation_queue.pop(0)
            self.execute_attack_with_animation(attacker, move)
            
        # Check if all animations finished
        if (self.animating and not self.attack_animation.active and 
            not self.animation_queue and not self.player1_flash.active and not self.player2_flash.active):
            self.animating = False
            # Check for winner after animations
            return self.check_winner()
            
        return None

    def execute_attack_with_animation(self, attacker, move_name):
        """Execute an attack with full animation"""
        # Determine target
        if attacker == self.player1_monster:
            target = self.player2_monster
            target_flash = self.player2_flash
        else:
            target = self.player1_monster
            target_flash = self.player1_flash

        # Get move data
        move_data = ABILITIES_DATA[move_name]
        
        # Start attack animation
        self.attack_animation.start_animation(move_name, move_data)
        
        # Calculate and apply damage
        damage = self.calculate_damage(attacker, target, move_data)
        target.take_damage(damage)
        
        # Start damage flash on target
        target_flash.start_flash()
        
        # Update UI health display
        self.battle_ui.update_health_display(
            self.player1_monster.health,
            self.player2_monster.health
        )
        
        print(f"{attacker.name} uses {move_name} on {target.name} for {damage} damage!")
        print(f"{target.name} health: {target.health}/{target.max_health}")

    def calculate_damage(self, attacker, target, move_data):
        """Calculate damage with type effectiveness"""
        base_damage = move_data['damage']
        move_element = move_data['element']
        
        # Get type effectiveness
        effectiveness = 1.0
        if move_element in ELEMENT_DATA and target.element in ELEMENT_DATA[move_element]:
            effectiveness = ELEMENT_DATA[move_element][target.element]
        
        # Get stats from monster data
        attacker_data = MONSTER_DATA[attacker.name]
        target_data = MONSTER_DATA[target.name]
        
        attack_stat = attacker_data['attack']
        defense_stat = target_data['defense']
        
        # Calculate final damage with stats
        damage = int(base_damage * effectiveness * (attack_stat / defense_stat))
        damage = max(1, damage)  # Minimum 1 damage
        
        return damage

    def check_winner(self):
        """Check if there's a winner"""
        if self.player1_monster.health <= 0:
            return self.player2_monster
        elif self.player2_monster.health <= 0:
            return self.player1_monster
        return None

    def draw_animations(self, surface):
        """Draw all active animations"""
        self.attack_animation.draw(surface)
        
    def get_monster_flash_state(self, monster):
        """Get flash state for a monster"""
        if monster == self.player1_monster:
            return self.player1_flash.should_flash()
        else:
            return self.player2_flash.should_flash()