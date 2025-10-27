"""
The main menu: plays a looping background video (if moviepy is available) and overlays
title text, character sprite, and two buttons (Start/Quit). Falls back to a static
starfield background if moviepy or the MP4 is unavailable.

Run interactive:
  python code/menu.py

Run a short automated validation (no clicks required):
  python code/menu.py --autotest
"""

import os
import sys
import math
import random
import subprocess
import pygame

pygame.init()
try:
    pygame.mixer.init()
except Exception:
    print("Warning: pygame.mixer failed to initialize; audio disabled.")

# --- Window ---
SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Theomachy")
clock = pygame.time.Clock()

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
VIDEO_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'background', 'theomachy-bg.mp4'))
CHAR_PATH = os.path.normpath(os.path.join(BASE_DIR, '..', 'images', 'simple', 'Charmadillo.png'))

# --- Fonts ---
try:
    title_font = pygame.font.Font(os.path.join(BASE_DIR, 'pixel_font.ttf'), 72)
except Exception:
    title_font = pygame.font.SysFont('Courier', 72)
button_font = pygame.font.SysFont('Courier', 36)

# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 140, 0)
DARK_ORANGE = (200, 100, 0)

# --- Load character (fallback to placeholder) ---
try:
    character_img = pygame.image.load(CHAR_PATH).convert_alpha()
    character_img = pygame.transform.scale(character_img, (150, 150))
except Exception as e:
    print(f"Warning: could not load character at {CHAR_PATH}: {e}")
    character_img = pygame.Surface((150, 150), pygame.SRCALPHA)
    pygame.draw.rect(character_img, (120, 120, 200), (0, 0, 150, 150))

# --- Video support ---
USE_VIDEO = False
VIDEO_CLIP = None
VIDEO_DURATION = 0
_VIDEO_START_MS = pygame.time.get_ticks()
try:
    # moviepy.layout changed between versions; try editor first then direct VideoFileClip path
    try:
        from moviepy.editor import VideoFileClip as _VFC
    except Exception:
        from moviepy.video.io.VideoFileClip import VideoFileClip as _VFC
    import numpy as np
    if os.path.exists(VIDEO_PATH):
        VIDEO_CLIP = _VFC(VIDEO_PATH)
        VIDEO_DURATION = VIDEO_CLIP.duration
        USE_VIDEO = True
        print(f"Loaded background video: {VIDEO_PATH} (duration={VIDEO_DURATION:.1f}s)")
    else:
        print(f"Background video not found at {VIDEO_PATH}; using static background.")
except Exception as e:
    print(f"Video disabled or moviepy not available: {e}; using static background.")

# --- Static fallback background (starfield) ---
bg_surface = pygame.Surface((SCREEN_W, SCREEN_H))
bg_surface.fill((18, 8, 28))
stars = [(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H)) for _ in range(120)]

# --- Background music (looping) ---
AUDIO_BG = os.path.normpath(os.path.join(BASE_DIR, '..', 'audio', 'halloween-spooky-music-413648.mp3'))
try:
    if os.path.exists(AUDIO_BG):
        pygame.mixer.music.load(AUDIO_BG)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
        print(f"Playing background music: {AUDIO_BG}")
    else:
        print(f"Background music not found at {AUDIO_BG}; continuing without music.")
except Exception as e:
    print(f"Could not play background music: {e}")


# --- Character slide in and bob ---
char_x = -character_img.get_width()
char_target_x = SCREEN_W - 320
char_y_base = SCREEN_H - 200
char_speed = 250.0
sliding = True
bob_amplitude = 6
bob_speed = 2.0

# --- Buttons ---
class Button:
    def __init__(self, text, x, y, w, h, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.hover = False

    def draw(self, surf):
        color = DARK_ORANGE if self.hover else ORANGE
        pygame.draw.rect(surf, color, self.rect)
        inner = self.rect.inflate(-6, -6)
        pygame.draw.rect(surf, BLACK, inner)
        txt = button_font.render(self.text, True, WHITE)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()

def start_game():
    # Launch main.py in a separate process and exit this menu
    main_py = os.path.normpath(os.path.join(BASE_DIR, 'main.py'))
    if os.path.exists(main_py):
        try:
            pygame.quit()
            subprocess.Popen([sys.executable, main_py])
            sys.exit(0)
        except Exception as e:
            print(f"Failed to launch main.py: {e}")
    else:
        print(f"main.py not found at {main_py}")

def quit_game():
    pygame.quit()
    sys.exit(0)

btn_w, btn_h = 260, 52
btn_x = SCREEN_W // 2 - btn_w // 2
btn_y = 100
btn_start = Button('Start Game', btn_x, btn_y, btn_w, btn_h, start_game)
btn_quit = Button('Quit', btn_x, btn_y + 74, btn_w, btn_h, quit_game)
buttons = [btn_start, btn_quit]

# --- Particles for simple campfire on right ---
particles = []
def create_fire_particle(x, y):
    return {
        'x': x + random.uniform(-6, 6),
        'y': y + random.uniform(-6, 6),
        'vx': random.uniform(-0.4, 0.4),
        'vy': random.uniform(-1.0, -0.4),
        'life': random.randint(30, 70),
        'max_life': 70,
        'w': random.randint(3, 7),
        'h': random.randint(2, 4),
        'color': random.choice([(255, 120, 40), (255, 80, 20), (255, 200, 40)])
    }
fire_origin = (SCREEN_W - 180, SCREEN_H - 120)

# --- Autotest ---
AUTOTEST = '--autotest' in sys.argv
AUTOTEST_LIMIT = 4.0
start_time = pygame.time.get_ticks() / 1000.0

# --- Main loop ---
running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        for b in buttons:
            b.handle_event(event)


    # update particles
    if random.random() < 0.6:
        particles.append(create_fire_particle(*fire_origin))
    for p in particles[:]:
        p['x'] += p['vx']
        p['y'] += p['vy']
        p['life'] -= 1
        if p['life'] <= 0:
            particles.remove(p)

    # update character slide
    if sliding:
        dir_x = char_target_x - char_x
        if abs(dir_x) < 4:
            char_x = char_target_x
            sliding = False
        else:
            step = char_speed * dt
            char_x += step if dir_x > 0 else -step

    # draw background (video or static)
    if USE_VIDEO and VIDEO_CLIP is not None:
        try:
            cur_ms = pygame.time.get_ticks()
            t = ((cur_ms - _VIDEO_START_MS) / 1000.0) % max(0.001, VIDEO_DURATION)
            frame = VIDEO_CLIP.get_frame(t)
            # ensure uint8
            try:
                import numpy as __np
                frame = (frame * 255).astype('uint8') if frame.dtype != 'uint8' and frame.max() <= 1.0 else frame.astype('uint8')
            except Exception:
                pass
            surf = pygame.image.frombuffer(frame.tobytes(), (frame.shape[1], frame.shape[0]), 'RGB')
            surf = pygame.transform.scale(surf, (SCREEN_W, SCREEN_H))
            screen.blit(surf, (0, 0))
        except Exception as e:
            print(f"Error rendering video frame: {e}; switching to static background.")
            USE_VIDEO = False
            screen.blit(bg_surface, (0, 0))
    else:
        screen.blit(bg_surface, (0, 0))
        for s in stars:
            pygame.draw.circle(screen, (220, 220, 240), s, 1)

    # campfire base and particles
    pygame.draw.rect(screen, (70, 40, 20), (fire_origin[0] - 18, fire_origin[1] + 6, 36, 8))
    for p in particles:
        alpha = int(255 * (p['life'] / p['max_life']))
        col = p['color'] + (alpha,)
        s = pygame.Surface((int(p['w']), int(p['h'])), pygame.SRCALPHA)
        s.fill(col)
        screen.blit(s, (int(p['x']), int(p['y'])))

    # character draw (bob when idle)
    bob_offset = 0
    if not sliding:
        bob_offset = math.sin(pygame.time.get_ticks() / 1000.0 * bob_speed * math.pi * 2) * bob_amplitude
    char_y = char_y_base + bob_offset
    screen.blit(character_img, (int(char_x), int(char_y)))


    # buttons
    for b in buttons:
        b.draw(screen)

    pygame.display.flip()

    if AUTOTEST:
        elapsed = pygame.time.get_ticks() / 1000.0 - start_time
        if elapsed >= AUTOTEST_LIMIT:
            print(f"Autotest: ran for {elapsed:.1f}s, exiting.")
            running = False

pygame.quit()
sys.exit(0)