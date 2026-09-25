# main.py
import pygame
import sys
import os
from character import Shadow
from maps.forest_zone import ForestZone
from scenes.title import TitleScreen

# --- CONSTANTES DE CONFIGURACIÓN Y UI ---
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
MAP_SELECT_BG = (50, 50, 150)
GAME_OVER_BG = (150, 0, 0)
GOAL_REACHED_BG = (50, 200, 50)
DISABLED_COLOR = (150, 150, 150)
FONT_SIZE_DEFAULT = 40
FONT_SIZE_TITLE = 80
FONT_SIZE_PAUSE = 100

# Placeholder para mapas no implementados
try:
    from maps.desert_zone import DesertZone
except ImportError:
    DesertZone = None
try:
    from maps.city_escape import CityEscape
except ImportError:
    CityEscape = None

# --- INICIALIZACIÓN BÁSICA ---
pygame.init()
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Shadow Fan Game")


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.clock = pygame.time.Clock()
        self.font_default = pygame.font.Font(None, FONT_SIZE_DEFAULT)
        self.font_title = pygame.font.Font(None, FONT_SIZE_TITLE)
        self.font_pause = pygame.font.Font(None, FONT_SIZE_PAUSE)

        # Estados del juego
        self.STATE_START_SCREEN = "start_screen"
        self.STATE_MAP_SELECT = "map_select"
        self.STATE_GAME_RUNNING = "game_running"
        self.STATE_GAME_PAUSED = "game_paused"
        self.STATE_GAME_OVER = "game_over"
        self.STATE_GOAL_REACHED = "goal_reached"
        self.current_state = self.STATE_START_SCREEN

        # Estado del jugador y nivel
        self.player_lives = 3
        self.last_confirmed_checkpoint_index = -1
        self.player = None
        self.current_map = None
        self.scroll_x = 0
        
        # Integración de 3 Mapas y 3 Stages
        self.current_stage = 1
        self.MAPS = self._get_map_list()
        
        self.walk_image_paths = self._get_shadow_walk_image_paths()
        
        self.map_selection = 0
        self.pause_options = ["Continuar", "Reiniciar Nivel", "Menú de Mapas", "Salir"]
        self.pause_selection = 0
        
        self.title_scene = TitleScreen(screen_width, screen_height)

    def _get_shadow_walk_image_paths(self):
        return [
            os.path.join('assets', 'characters', 'shadow', 'sprites', 'walk', f'walkshadow{i}.png')
            for i in range(1, 4)
        ]
        
    def _get_map_list(self):
        return [
            {"name": "Forest Zone", "class": ForestZone},
            {"name": "Desert Zone", "class": DesertZone, "disabled": DesertZone is None},
            {"name": "City Escape", "class": CityEscape, "disabled": CityEscape is None},
        ]

    def reset_game(self, map_class=None, from_death=False, next_stage=False):
        """Reinicia el estado del juego, avanza de stage o respawnea al jugador."""
        if map_class:
            self.current_stage = 1
            self.current_map = map_class(self.screen_width, self.screen_height, stage=self.current_stage)
            self.last_confirmed_checkpoint_index = -1
            self.player_lives = 3
        elif next_stage and self.current_map:
            self.current_stage += 1
            if self.current_stage > 3:
                # Si completa el Stage 3, vuelve al menú
                self.current_state = self.STATE_MAP_SELECT
                return
            # Cargar el siguiente Stage del mismo mapa
            self.current_map = self.current_map.__class__(self.screen_width, self.screen_height, stage=self.current_stage)
            self.last_confirmed_checkpoint_index = -1
        elif not self.current_map:
            return

        if not from_death and not next_stage:
            self.last_confirmed_checkpoint_index = -1

        start_pos = self.current_map.get_respawn_position(self.last_confirmed_checkpoint_index)
        self.player = Shadow(start_pos, self.walk_image_paths)
        self.scroll_x = max(0, start_pos[0] - self.screen_width // 4)
        self.current_state = self.STATE_GAME_RUNNING
        
    def player_death(self):
        self.player_lives -= 1
        if self.player_lives <= 0:
            self.current_state = self.STATE_GAME_OVER
        else:
            self.reset_game(from_death=True)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False 
            
            if self.current_state == self.STATE_GAME_RUNNING:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.current_state = self.STATE_GAME_PAUSED
                if self.player:
                    self.player.handle_event(event)
            
            elif self.current_state == self.STATE_GAME_PAUSED:
                self.handle_pause_events(event)

            elif self.current_state == self.STATE_GAME_OVER:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.current_state = self.STATE_MAP_SELECT

            elif self.current_state == self.STATE_GOAL_REACHED:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    # Avanzar al siguiente Stage
                    self.reset_game(next_stage=True)
                    
            elif self.current_state == self.STATE_START_SCREEN:
                next_action = self.title_scene.handle_event(event)
                if next_action == "MAP_SELECT":
                    self.current_state = self.STATE_MAP_SELECT

            elif self.current_state == self.STATE_MAP_SELECT:
                self.handle_map_select_events(event)

        return True

    def handle_pause_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.current_state = self.STATE_GAME_RUNNING
            elif event.key == pygame.K_UP:
                self.pause_selection = (self.pause_selection - 1) % len(self.pause_options)
            elif event.key == pygame.K_DOWN:
                self.pause_selection = (self.pause_selection + 1) % len(self.pause_options)
            elif event.key == pygame.K_RETURN:
                if self.pause_selection == 0:  
                    self.current_state = self.STATE_GAME_RUNNING
                elif self.pause_selection == 1: 
                    self.player_lives -= 1 
                    self.reset_game(map_class=self.current_map.__class__)
                elif self.pause_selection == 2: 
                    self.current_state = self.STATE_MAP_SELECT
                elif self.pause_selection == 3: 
                    pygame.quit()
                    sys.exit()

    def handle_map_select_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.map_selection = (self.map_selection - 1) % len(self.MAPS)
            elif event.key == pygame.K_DOWN:
                self.map_selection = (self.map_selection + 1) % len(self.MAPS)
            elif event.key == pygame.K_RETURN:
                selected_map_info = self.MAPS[self.map_selection]
                if not selected_map_info.get('disabled', False):
                    self.reset_game(selected_map_info['class'])
                    self.map_selection = 0 

    def update_game(self):
        if not self.player or not self.current_map:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

        # LÓGICA DE COLISIÓN CORREGIDA
        ground_y = 2000 # Caída al vacío por defecto
        player_rect = self.player.rect
        
        if hasattr(self.current_map, 'ground_platforms'):
            for rect in self.current_map.ground_platforms:
                # Comprobar si el jugador está horizontalmente dentro de la plataforma
                if player_rect.right > rect.left and player_rect.left < rect.right:
                    # Comprobar colisión desde arriba
                    if player_rect.bottom <= rect.top + 30 and self.player.y_velocity >= 0:
                        ground_y = min(ground_y, rect.top)

        # Actualizar jugador aplicando gravedad y límite de suelo
        self.player.update(ground_y)

        # Actualización de Scroll (Seguimiento de cámara)
        target_scroll_x = self.player.rect.x - self.screen_width // 4
        self.scroll_x += (target_scroll_x - self.scroll_x) * 0.1
        if hasattr(self.current_map, 'LEVEL_WIDTH'):
            self.scroll_x = max(0, min(self.scroll_x, self.current_map.LEVEL_WIDTH - self.screen_width))

        # Comprobación de Muerte (Caer al vacío)
        if hasattr(self.current_map, 'VOID_Y') and self.player.rect.top > self.current_map.VOID_Y:
            self.player_death()
            return

        # Comprobación de Meta
        if hasattr(self.current_map, 'get_goal_rect') and self.current_map.get_goal_rect().colliderect(self.player.rect):
            self.current_state = self.STATE_GOAL_REACHED
            return
                
    def update(self):
        if self.current_state == self.STATE_GAME_RUNNING:
            self.update_game()
        elif self.current_state == self.STATE_START_SCREEN:
            self.title_scene.update()

    # --- MÉTODOS DE DIBUJO ---
    def draw_running_game(self):
        self.current_map.draw(self.screen, self.scroll_x)
        self.player.draw(self.screen, self.scroll_x)
        
        # UI: Vidas y Stage
        lives_text = self.font_default.render(f"VIDAS: {self.player_lives}", True, WHITE)
        self.screen.blit(lives_text, (20, 20))
        stage_text = self.font_default.render(f"ACTO {self.current_stage}", True, WHITE)
        self.screen.blit(stage_text, (self.screen_width - 150, 20))

    def draw_pause_menu(self):
        self.draw_running_game()
        pause_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        pause_surface.fill((0, 0, 0, 180)) 
        self.screen.blit(pause_surface, (0, 0))

        title_text = self.font_pause.render("PAUSA", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width / 2, 100))
        self.screen.blit(title_text, title_rect)
        
        for i, option in enumerate(self.pause_options):
            color = GOLD if i == self.pause_selection else WHITE
            text = self.font_default.render(option, True, color)
            text_rect = text.get_rect(center=(self.screen_width / 2, 250 + i * 60))
            self.screen.blit(text, text_rect)

    def draw_map_select_screen(self):
        self.screen.fill(MAP_SELECT_BG)
        title_text = self.font_title.render("SELECCIÓN DE NIVEL", True, WHITE)
        title_rect = title_text.get_rect(center=(self.screen_width / 2, 100))
        self.screen.blit(title_text, title_rect)

        for i, map_info in enumerate(self.MAPS):
            color = GOLD if i == self.map_selection else WHITE
            text = self.font_default.render(map_info['name'], True, color)
            text_rect = text.get_rect(center=(self.screen_width / 2, 250 + i * 60))
            self.screen.blit(text, text_rect)
            if map_info.get('disabled', False):
                 disabled_text = self.font_default.render("(PRÓXIMAMENTE)", True, DISABLED_COLOR)
                 disabled_rect = disabled_text.get_rect(midleft=(text_rect.right + 20, text_rect.centery))
                 self.screen.blit(disabled_text, disabled_rect)
                 
    def draw_game_over_screen(self):
        self.screen.fill(GAME_OVER_BG)
        text = self.font_title.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(self.screen_width / 2, self.screen_height / 2))
        self.screen.blit(text, text_rect)
        text_restart = self.font_default.render("Presiona ENTER para volver al menú", True, WHITE)
        text_restart_rect = text_restart.get_rect(center=(self.screen_width / 2, self.screen_height / 2 + 100))
        self.screen.blit(text_restart, text_restart_rect)

    def draw_goal_reached_screen(self):
        self.screen.fill(GOAL_REACHED_BG)
        text = self.font_title.render(f"¡ACTO {self.current_stage} COMPLETADO!", True, WHITE)
        text_rect = text.get_rect(center=(self.screen_width / 2, self.screen_height / 2))
        self.screen.blit(text, text_rect)
        
        msg = "Presiona ENTER para avanzar" if self.current_stage < 3 else "Presiona ENTER para volver al menú"
        text_continue = self.font_default.render(msg, True, WHITE)
        text_continue_rect = text_continue.get_rect(center=(self.screen_width / 2, self.screen_height / 2 + 100))
        self.screen.blit(text_continue, text_continue_rect)
        
    def draw_start_screen(self):
        self.title_scene.draw(self.screen)
        
    def draw(self):
        if self.current_state == self.STATE_START_SCREEN:
            self.draw_start_screen()
        elif self.current_state == self.STATE_MAP_SELECT:
            self.draw_map_select_screen()
        elif self.current_state == self.STATE_GAME_RUNNING:
            self.draw_running_game()
        elif self.current_state == self.STATE_GAME_PAUSED:
            self.draw_pause_menu()
        elif self.current_state == self.STATE_GAME_OVER:
            self.draw_game_over_screen()
        elif self.current_state == self.STATE_GOAL_REACHED:
            self.draw_goal_reached_screen()

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if not running:
                break
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    game = Game(screen)
    game.current_state = game.STATE_START_SCREEN
    game.run()