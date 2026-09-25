# scenes/title.py
import pygame
import sys
import os
import random

# --- Colores ---
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
PURPLE_DARK = (20, 0, 40)
SHADOW_TITLE_COLOR = (255, 50, 50)

class TitleScreen:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.shadow_frames = self._load_shadow_frames()
        self.frame_index = 0
        self.animation_interval = 250  # Intervalo en milisegundos
        self.last_update_time = 0
        
        self.font_title = pygame.font.Font(None, 120)
        self.font_start = pygame.font.Font(None, 60)
        self.text_alpha = 255
        self.alpha_direction = -1
        self.blink_speed = 5
        
        self.stars = self._generate_stars(150)
        
    def reset(self):
        self.text_alpha = 255
        self.alpha_direction = -1
        self.last_update_time = pygame.time.get_ticks()

    def _load_shadow_frames(self):
        frames = []
        base_dir = os.path.join('assets', 'characters', 'pressstart')
        for i in range(1, 5):
            path = os.path.join(base_dir, f'startgame-shadow{i}.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                target_height = int(self.screen_height * 0.7)
                scale_factor = target_height / img.get_height()
                new_width = int(img.get_width() * scale_factor)
                frames.append(pygame.transform.scale(img, (new_width, target_height)))
            except pygame.error as e:
                print(f"ADVERTENCIA: No se pudo cargar {path}: {e}")
                frames.append(pygame.Surface((150, int(self.screen_height * 0.7)), pygame.SRCALPHA))
        return frames

    def _generate_stars(self, count):
        return [{
            'x': random.randint(0, self.screen_width),
            'y': random.randint(0, self.screen_height),
            'size': random.randint(1, 3),
            'speed': random.uniform(0.1, 0.5)
        } for _ in range(count)]
        
    def update(self):
        current_time = pygame.time.get_ticks()
        
        if current_time - self.last_update_time > self.animation_interval:
            self.frame_index = (self.frame_index + 1) % len(self.shadow_frames)
            self.last_update_time = current_time
            
        self.text_alpha += self.alpha_direction * self.blink_speed
        if not 0 <= self.text_alpha <= 255:
            self.alpha_direction *= -1
            self.text_alpha = max(0, min(255, self.text_alpha))
            
        for star in self.stars:
            star['x'] -= star['speed']
            if star['x'] < 0:
                star['x'] = self.screen_width
                star['y'] = random.randint(0, self.screen_height)
        
    def draw(self, surface):
        surface.fill(PURPLE_DARK)
        for star in self.stars:
            pygame.draw.circle(surface, WHITE, (int(star['x']), int(star['y'])), star['size'])
            
        if self.shadow_frames:
            shadow_image = self.shadow_frames[self.frame_index]
            shadow_rect = shadow_image.get_rect(center=(self.screen_width // 2, self.screen_height * 0.55))
            surface.blit(shadow_image, shadow_rect)
            
        title_text = self.font_title.render("SHADOW", True, SHADOW_TITLE_COLOR)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        surface.blit(title_text, title_rect)

        start_text_render = self.font_start.render("PRESS START", True, GOLD)
        start_text_render.set_alpha(self.text_alpha)
        start_rect = start_text_render.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        surface.blit(start_text_render, start_rect)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            return "MAP_SELECT"
        return None