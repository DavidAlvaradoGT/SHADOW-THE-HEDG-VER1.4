# player.py (ejemplo simplificado, si no lo tienes así)
import pygame

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((255, 0, 255)) # Color para el personaje
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vx = 0
        self.vy = 0
        self.speed = 5
        self.jump_power = -15 # Negativo para saltar hacia arriba
        self.gravity = 0.8
        self.on_ground = False
        self.lives = 3 # Ejemplo

    def apply_gravity(self):
        self.vy += self.gravity
        # Limitar la velocidad de caída máxima
        if self.vy > 20:
            self.vy = 20

    def jump(self):
        if self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False # Ya no está en el suelo

    def move_left(self):
        self.vx = -self.speed

    def move_right(self):
        self.vx = self.speed

    def stop_x(self):
        self.vx = 0

    def update(self):
        self.apply_gravity()

        self.rect.x += self.vx
        self.rect.y += self.vy

        # Esto solo es para depuración visual, la colisión con el suelo se maneja en main.py
        # Si el personaje cae por debajo de una cierta línea sin colisionar
        # if self.rect.top > 800: # Ejemplo de caída
        #     self.rect.topleft = (50, 600)
        #     self.vy = 0
        #     self.on_ground = True
        
    def lose_life(self):
        self.lives -= 1
        print(f"VIDAS: {self.lives}")
        if self.lives <= 0:
            print("¡Game Over!")
            # Aquí puedes añadir la lógica para Game Over