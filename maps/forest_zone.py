# maps/forest_zone.py
import pygame

class ForestZone:
    def __init__(self, screen_width, screen_height, stage=1):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.stage = stage # 1, 2 o 3 (Acto 1, Acto 2, Acto 3)

        # Dimensiones y físicas del nivel
        self.LEVEL_WIDTH = 6000
        self.VOID_Y = 1200 # Límite de caída (Muerte)
        
        # Colores estilo Retro (Basado en la referencia visual de Sonic 1)
        self.SKY_COLOR = (0, 0, 128)      # Azul oscuro
        self.GRASS_COLOR = (0, 180, 0)    # Verde brillante
        self.DIRT_DARK = (100, 50, 0)     # Café oscuro
        self.DIRT_LIGHT = (205, 133, 63)  # Café claro / Naranja
        self.TILE_SIZE = 32
        self.GRASS_HEIGHT = 32

        # Generar el diseño del mapa dependiendo del Acto (Stage)
        self.ground_platforms = []
        self.build_stage()

    def build_stage(self):
        """Construye las plataformas del nivel según el Acto (Stage) actual."""
        if self.stage == 1:
            # Stage 1: Recorrido básico con saltos
            self.ground_platforms = [
                pygame.Rect(0, 500, 1200, 500),      # Suelo inicial
                pygame.Rect(1400, 400, 800, 600),    # Plataforma media
                pygame.Rect(2400, 500, 1000, 500),   # Suelo bajo
                pygame.Rect(3600, 300, 600, 700),    # Plataforma alta
                pygame.Rect(4400, 500, 1600, 500)    # Zona final
            ]
        elif self.stage == 2:
            # Stage 2: Más vacíos y saltos de precisión
            self.ground_platforms = [
                pygame.Rect(0, 500, 800, 500),
                pygame.Rect(1000, 400, 500, 600),
                pygame.Rect(1800, 300, 500, 700),
                pygame.Rect(2800, 500, 2000, 500)
            ]
        elif self.stage == 3:
            # Stage 3: Tramo largo (Preparado para jefe o final rápido)
            self.ground_platforms = [
                pygame.Rect(0, 500, 4000, 500),
            ]

    def get_respawn_position(self, checkpoint_index=-1):
        """Devuelve las coordenadas (X, Y) donde aparece Shadow según el Stage."""
        if self.stage == 1:
            return (100, 300)
        elif self.stage == 2:
            return (100, 300)
        elif self.stage == 3:
            return (100, 300)
        return (100, 300)

    def get_ground_level(self):
        """Nivel de suelo base de emergencia."""
        return 2000

    def get_goal_rect(self):
        """Área de meta al final del nivel."""
        if self.stage == 1:
            return pygame.Rect(5800, 300, 100, 200) 
        return pygame.Rect(3800, 300, 100, 200)

    def draw(self, surface, scroll_x):
        """Dibuja el nivel completo con el estilo retro de cuadros."""
        # 1. Fondo (Cielo azul oscuro)
        surface.fill(self.SKY_COLOR)

        # 2. Dibujar Suelo (Tierra a cuadros y pasto)
        for rect in self.ground_platforms:
            draw_rect = rect.copy()
            draw_rect.x -= scroll_x
            
            # Solo dibujar si está en pantalla (Optimización)
            if draw_rect.right > 0 and draw_rect.left < self.screen_width:
                
                # A. Base de tierra
                dirt_rect = pygame.Rect(draw_rect.x, draw_rect.y + self.GRASS_HEIGHT, draw_rect.width, draw_rect.height - self.GRASS_HEIGHT)
                
                # B. Patrón de cuadros (Checkerboard)
                for y_offset in range(0, dirt_rect.height, self.TILE_SIZE):
                    row = y_offset // self.TILE_SIZE
                    for x_offset in range(0, dirt_rect.width, self.TILE_SIZE):
                        col = x_offset // self.TILE_SIZE
                        
                        # Alternar colores basado en la suma de fila y columna
                        color = self.DIRT_DARK if (row + col) % 2 == 0 else self.DIRT_LIGHT
                        
                        tile_rect = pygame.Rect(dirt_rect.x + x_offset, dirt_rect.y + y_offset, self.TILE_SIZE, self.TILE_SIZE)
                        clipped_rect = tile_rect.clip(dirt_rect) # Evita que los cuadros se salgan de la plataforma
                        pygame.draw.rect(surface, color, clipped_rect)

                # C. Pasto superior
                grass_rect = pygame.Rect(draw_rect.x, draw_rect.y, draw_rect.width, self.GRASS_HEIGHT)
                pygame.draw.rect(surface, self.GRASS_COLOR, grass_rect)
                
                # D. Detalle de picos en el pasto
                for i in range(0, grass_rect.width, 16):
                    spike_points = [
                        (grass_rect.x + i, grass_rect.y),
                        (grass_rect.x + i + 8, grass_rect.y - 8),
                        (grass_rect.x + i + 16, grass_rect.y)
                    ]
                    pygame.draw.polygon(surface, self.GRASS_COLOR, spike_points)

        # 3. Dibujar la meta (Caja amarilla temporal)
        goal_draw_rect = self.get_goal_rect().copy()
        goal_draw_rect.x -= scroll_x
        pygame.draw.rect(surface, (255, 215, 0), goal_draw_rect)