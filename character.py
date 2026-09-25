# character.py
import pygame
import os
import math
import time 

class Shadow(pygame.sprite.Sprite):
    # --- CONSTANTES DE FÍSICA Y MOVIMIENTO ---
    WALK_HEIGHT = 64
    ROLL_HEIGHT = 40
    
    # Gravedad y Salto (AJUSTADO para caída más rápida y menos 'flotante')
    GRAVITY = 0.8       # Aumentado para menos 'flotación'.
    JUMP_VELOCITY = -15 # Ajustado para un salto balanceado.
    
    # Movimiento horizontal (AJUSTADO para mejor respuesta)
    PLAYER_SPEED = 7
    ACCELERATION = 1.2
    FRICTION = 0.9      # Aumentado para mejor control en el suelo.
    
    # Carga del Spin Roll
    CHARGE_RATE = 2
    MAX_CHARGE = 100
    MIN_ROLL_VELOCITY = 10
    MAX_ROLL_VELOCITY = 25
    ROLL_DECELERATION = 0.99
    ROLL_GROUND_FRICTION = 0.98
    
    # Dash Aéreo
    DASH_VELOCITY = 30
    DASH_DURATION_MS = 250
    DASH_COOLDOWN_MS = 1000

    def __init__(self, midbottom_pos, walk_image_paths):
        super().__init__()
        
        # --- Carga de Imágenes ---
        self.walk_frames = self._load_and_scale_images(walk_image_paths, self.WALK_HEIGHT)
        roll_path = os.path.join('assets', 'characters', 'shadow', 'sprites', 'roll', 'rollshadow.png')
        self.roll_frames = self._load_and_scale_images([roll_path], self.ROLL_HEIGHT) 
        
        self.idle_frame = self.walk_frames[0]
        self.image = self.idle_frame
        self.rect = self.image.get_rect(midbottom=midbottom_pos)
        
        # --- Estado de Movimiento ---
        self.x_velocity = 0
        self.y_velocity = 0
        self.on_ground = True
        self.facing_right = True
        
        # --- Banderas de Estado (Flags) ---
        self.is_jumping = False
        self.is_crouching = False
        self.is_rolling = False
        self.is_dashing = False

        # --- Temporizadores y Carga ---
        self.roll_charge = 0
        self.dash_end_time = 0
        self.dash_cooldown_end_time = 0

        # --- Animación ---
        self.animation_interval_ms = 100
        self.frame_index = 0
        self.last_update_time = 0

    def _load_and_scale_images(self, paths, target_height):
        images = []
        for path in paths:
            try:
                image = pygame.image.load(path).convert_alpha()
                original_width, original_height = image.get_size()
                scale_factor = target_height / original_height
                new_width = int(original_width * scale_factor)
                scaled_image = pygame.transform.scale(image, (new_width, target_height))
                images.append(scaled_image)
            except pygame.error as e:
                print(f"Error al cargar imagen {path}: {e}")
                fallback_image = pygame.Surface((32, target_height), pygame.SRCALPHA)
                fallback_image.fill((255, 0, 0, 180))
                images.append(fallback_image)
        return images

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.on_ground and not self.is_crouching:
                self.jump()
            elif event.key == pygame.K_DOWN and self.on_ground:
                self.crouch()
            elif event.key == pygame.K_LSHIFT:
                self.start_dash()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_DOWN and self.is_crouching:
                self.release_roll()

    def handle_input(self, keys):
        if self.is_dashing or self.is_rolling:
            return

        if self.is_crouching:
            return

        target_speed = 0
        if keys[pygame.K_LEFT]:
            target_speed = -self.PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            target_speed = self.PLAYER_SPEED
            self.facing_right = True

        if target_speed != 0:
            if target_speed > 0:
                self.x_velocity = min(self.x_velocity + self.ACCELERATION, target_speed)
            else:
                self.x_velocity = max(self.x_velocity - self.ACCELERATION, target_speed)
        else:
            self.x_velocity *= self.FRICTION
            if abs(self.x_velocity) < 0.5:
                self.x_velocity = 0

    def jump(self):
        self.y_velocity = self.JUMP_VELOCITY
        self.on_ground = False
        self.is_jumping = True
        self.is_crouching = False 

    def crouch(self):
        if not self.is_rolling:
            self.is_crouching = True
            current_midbottom = self.rect.midbottom
            self.image = self.roll_frames[0] 
            self.rect = self.image.get_rect(midbottom=current_midbottom)

    def release_roll(self):
        self.is_crouching = False
        self.image = self.idle_frame 
        
        if self.roll_charge > 0:
            roll_speed = self.MIN_ROLL_VELOCITY + (self.roll_charge / self.MAX_CHARGE) * (self.MAX_ROLL_VELOCITY - self.MIN_ROLL_VELOCITY)
            if not self.facing_right:
                roll_speed *= -1
            
            self.x_velocity = roll_speed
            self.is_rolling = True
        
        self.roll_charge = 0
        current_midbottom = self.rect.midbottom
        self.rect = self.idle_frame.get_rect(midbottom=current_midbottom)

    def start_dash(self):
        current_time = pygame.time.get_ticks()
        if not self.on_ground and (current_time > self.dash_cooldown_end_time):
            self.is_dashing = True
            self.dash_end_time = current_time + self.DASH_DURATION_MS
            self.y_velocity = 0 
            self.x_velocity = self.DASH_VELOCITY if self.facing_right else -self.DASH_VELOCITY

    def apply_gravity(self, ground_level):
        if self.is_dashing:
            return

        if not self.on_ground:
            self.y_velocity += self.GRAVITY
            if self.y_velocity > 20:
                self.y_velocity = 20

        self.rect.y += int(self.y_velocity)
        
        if self.rect.bottom > ground_level:
            self.rect.bottom = ground_level
            self.y_velocity = 0
            self.on_ground = True
            self.is_jumping = False
            self.is_rolling = self.is_rolling 

    def apply_movement(self, keys):
        self.rect.x += int(self.x_velocity)
    
    def update(self, ground_level):
        current_time = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        # 1. Manejo del Dash Aéreo
        if self.is_dashing:
            if current_time < self.dash_end_time:
                self.rect.x += int(self.x_velocity)
                self.rect.y += int(self.y_velocity)
                return
            else:
                self.is_dashing = False
                self.dash_cooldown_end_time = current_time + self.DASH_COOLDOWN_MS
                self.y_velocity = 0
                self.rect.x += int(self.x_velocity) 

        # 2. Carga del Roll
        if self.is_crouching:
            self.roll_charge = min(self.MAX_CHARGE, self.roll_charge + self.CHARGE_RATE)
            self.animate()
            return
        
        # 3. Movimiento del Roll
        if self.is_rolling:
            friction = self.ROLL_GROUND_FRICTION if self.on_ground else self.ROLL_DECELERATION
            self.x_velocity *= friction
            if abs(self.x_velocity) < 1.0 and self.on_ground:
                self.is_rolling = False
            self.rect.x += int(self.x_velocity)
        else:
            # 4. Movimiento normal
            self.apply_movement(keys)
        
        # 5. Gravedad
        self.apply_gravity(ground_level)
            
        # 6. Animación
        self.animate()

    def animate(self):
        current_time = pygame.time.get_ticks()
        if current_time > self.last_update_time + self.animation_interval_ms:
            self.last_update_time = current_time
            
            if self.is_rolling or self.is_crouching or self.is_jumping or self.is_dashing:
                self.frame_index = (self.frame_index + 1) % len(self.roll_frames)
                self.image = self.roll_frames[self.frame_index]
                if len(self.roll_frames) == 1:
                    self.image = self.roll_frames[0]
            elif abs(self.x_velocity) > 0.5 and self.on_ground:
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
                self.image = self.walk_frames[self.frame_index]
            else:
                self.frame_index = 0
                self.image = self.idle_frame

            if self.is_crouching or self.is_rolling:
                if self.rect.height != self.ROLL_HEIGHT:
                    current_midbottom = self.rect.midbottom
                    self.rect = self.image.get_rect(midbottom=current_midbottom)
            elif self.rect.height != self.WALK_HEIGHT:
                current_midbottom = self.rect.midbottom
                self.rect = self.idle_frame.get_rect(midbottom=current_midbottom)

    def draw(self, surface, scroll_x):
        draw_x = self.rect.x - scroll_x
        image_to_draw = pygame.transform.flip(self.image, not self.facing_right, False)
        surface.blit(image_to_draw, (draw_x, self.rect.y))
        
        if self.is_crouching:
            charge_bar_width = 50
            charge_fill = int((self.roll_charge / self.MAX_CHARGE) * charge_bar_width)
            
            bar_x = draw_x + self.rect.width // 2 - charge_bar_width // 2
            bar_y = self.rect.top - 15
            
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, charge_bar_width, 10), 0)
            pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, charge_fill, 10), 0)
            pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, charge_bar_width, 10), 1)