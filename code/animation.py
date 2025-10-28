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
        
        # Attack animation
        self.attack_animation = AttackAnimation()
    
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

    def update(self, dt):
        """Update all animations"""
        self.update_attack_animation(dt)
        
    def draw(self, screen):
        """Draw all animations"""
        self.draw_attack_animation(screen)
        # Draw damage flash if active
        if self.damage_flash.should_flash():
            screen.fill((255, 0, 0), special_flags=pygame.BLEND_ADD)
        
class AttackAnimation:
    def __init__(self):
        self.active = False
        self.attack_name = None
        self.image = None
        self.duration = 0
        self.max_duration = 2000  # 2 seconds
        self.alpha = 255
        
    def start_animation(self, attack_name, ability_data):
        """Start an attack animation"""
        self.active = True
        self.attack_name = attack_name
        self.duration = 0
        self.alpha = 255
        
        # Use the animation field from ability data for image filename
        animation_name = ability_data.get('animation', attack_name)
        
        # Load attack image
        image_path = f'images/attacks/{animation_name}.png'
        if os.path.exists(image_path):
            self.image = pygame.image.load(image_path).convert_alpha()
            # Scale image to be clearly visible
            self.image = pygame.transform.smoothscale(self.image, (300, 300))
        else:
            print(f"Attack image not found: {image_path}")
            self.image = None
            
        # Play attack sound - try both mp3 and wav
        audio_paths = [
            f'audio/{animation_name}.mp3',
            f'audio/{animation_name}.wav',
            f'audio/{attack_name}.mp3',
            f'audio/{attack_name}.wav'
        ]
        
        for audio_path in audio_paths:
            if os.path.exists(audio_path):
                try:
                    sound = pygame.mixer.Sound(audio_path)
                    sound.play()
                    break
                except Exception as e:
                    print(f"Could not play sound {audio_path}: {e}")
                    continue
    
    def update(self, dt):
        """Update animation"""
        if not self.active:
            return
            
        self.duration += dt * 1000  # Convert to milliseconds
        
        # Fade out towards the end
        if self.duration > self.max_duration * 0.7:
            fade_progress = (self.duration - self.max_duration * 0.7) / (self.max_duration * 0.3)
            self.alpha = int(255 * (1 - fade_progress))
        
        # End animation
        if self.duration >= self.max_duration:
            self.active = False
            
    def draw(self, surface):
        """Draw the attack animation"""
        if not self.active or not self.image:
            return
            
        # Create a surface with alpha
        temp_surface = self.image.copy()
        temp_surface.set_alpha(self.alpha)
        
        # Center the image on screen
        rect = temp_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(temp_surface, rect)

class DamageFlash:
    def __init__(self):
        self.active = False
        self.duration = 0
        self.max_duration = 1000  # 1 second
        self.flash_interval = 100  # Flash every 100ms
        self.show_flash = False
        
    def start_flash(self):
        """Start damage flash effect"""
        self.active = True
        self.duration = 0
        self.show_flash = True
        
    def update(self, dt):
        """Update flash effect"""
        if not self.active:
            return
            
        self.duration += dt * 1000  # Convert to milliseconds
        
        # Toggle flash every interval
        if int(self.duration / self.flash_interval) % 2 == 0:
            self.show_flash = True
        else:
            self.show_flash = False
            
        # End flash
        if self.duration >= self.max_duration:
            self.active = False
            self.show_flash = False
            
    def should_flash(self):
        """Returns True if should show red flash"""
        return self.active and self.show_flash