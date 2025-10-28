import pygame
import math
import os

class Animation:
    def __init__(self):
        # Load all attack animations
        self.attack_sprites = {}
        self.attack_sounds = {}
        self.load_attack_assets()
        
        # Animation states
        self.current_animation = None
        self.animation_frame = 0
        self.animation_done = True
        
        # Monster animation properties
        self.bob_offset = 0
        self.bob_speed = 2
        self.bob_amplitude = 10
        self.bob_time = 0
        
        # Hit animation properties
        self.hit_offset = 0
        self.hit_return_speed = 0.2
        self.max_hit_offset = 30
        
    def load_attack_assets(self):
        """Load all attack images and sounds"""
        # Load attack images
        attack_types = ['fire', 'ice', 'scratch', 'explosion', 'green', 'splash']
        for attack in attack_types:
            try:
                img_path = os.path.join('images', 'attacks', f'{attack}.png')
                self.attack_sprites[attack] = pygame.image.load(img_path).convert_alpha()
            except Exception as e:
                print(f"Failed to load attack sprite {attack}: {e}")
                
        # Load attack sounds
        for attack in attack_types:
            try:
                sound_path = os.path.join('audio', f'{attack}.wav')
                if not os.path.exists(sound_path):
                    sound_path = os.path.join('audio', f'{attack}.mp3')
                self.attack_sounds[attack] = pygame.mixer.Sound(sound_path)
            except Exception as e:
                print(f"Failed to load attack sound {attack}: {e}")
    
    def start_attack_animation(self, attack_type, attacker_pos, target_pos):
        """Start an attack animation sequence"""
        if attack_type in self.attack_sprites:
            self.current_animation = {
                'type': attack_type,
                'sprite': self.attack_sprites[attack_type],
                'start_pos': attacker_pos,
                'target_pos': target_pos,
                'progress': 0
            }
            self.animation_done = False
            # Play attack sound
            if attack_type in self.attack_sounds:
                self.attack_sounds[attack_type].play()
    
    def update_monster_bob(self, dt):
        """Update the bobbing animation offset"""
        self.bob_time += dt * self.bob_speed
        self.bob_offset = math.sin(self.bob_time) * self.bob_amplitude
        return self.bob_offset
    
    def update_hit_animation(self, is_hit):
        """Update the hit reaction animation"""
        if is_hit and self.hit_offset < self.max_hit_offset:
            self.hit_offset = self.max_hit_offset
        elif self.hit_offset > 0:
            self.hit_offset *= (1 - self.hit_return_speed)
        return self.hit_offset
    
    def update_attack_animation(self, dt):
        """Update the current attack animation"""
        if self.current_animation is None:
            return True
            
        self.current_animation['progress'] += dt
        
        # Animation completed
        if self.current_animation['progress'] >= 1.0:
            self.current_animation = None
            self.animation_done = True
            return True
            
        return False
    
    def draw_attack_animation(self, screen):
        """Draw the current attack animation"""
        if self.current_animation is None:
            return
            
        anim = self.current_animation
        progress = anim['progress']
        
        # Calculate current position
        start_x, start_y = anim['start_pos']
        target_x, target_y = anim['target_pos']
        current_x = start_x + (target_x - start_x) * progress
        current_y = start_y + (target_y - start_y) * progress
        
        # Draw the attack sprite
        sprite = anim['sprite']
        sprite_rect = sprite.get_rect(center=(current_x, current_y))
        screen.blit(sprite, sprite_rect)