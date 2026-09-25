# maps/city_escape.py
import pygame

class CityEscape:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.name = "city_escape"

        self.level_data = {
            "layers": [
                {"type": "solid_color", "color": (40, 40, 60)},
                {
                    "type": "rects", "color": (255, 255, 224), "speed": 0.05,
                    "elements": [
                        [100, 50, 2, 2], [250, 80, 1, 1], [400, 40, 2, 2], [550, 120, 1, 1],
                        [700, 60, 3, 3], [850, 150, 1, 1], [1000, 70, 2, 2], [1150, 130, 1, 1],
                    ]
                },
                {"type": "circles", "color": (240, 240, 240), "speed": 0.1, "elements": [[200, 150, 60]]},
                {
                    "type": "rects", "color": (80, 80, 90), "speed": 0.2,
                    "elements": [
                        [50, 150, 100, 350], [200, 200, 80, 300], [350, 100, 120, 400],
                        [600, 250, 90, 250], [800, 180, 150, 320], [1100, 220, 100, 280],
                    ],
                },
                {
                    "type": "rects", "color": (255, 255, 0, 150), "speed": 0.2,
                    "elements": [
                        [60, 160, 20, 20], [90, 160, 20, 20], [60, 200, 20, 20], [90, 200, 20, 20],
                        [360, 120, 25, 40], [405, 120, 25, 40], [360, 180, 25, 40], [405, 180, 25, 40],
                        [810, 200, 30, 30], [860, 200, 30, 30], [810, 250, 30, 30], [860, 250, 30, 30],
                    ]
                },
                {"type": "solid_rect", "color": (50, 50, 50), "speed": 1.0, "rect": [0, 500, 1280, 220]},
            ],
        }
        self.layers = self.level_data['layers']
        self._calculate_pattern_widths()

    def get_ground_level(self):
        for layer in self.layers:
            if layer.get('type') == 'solid_rect':
                return layer['rect'][1]
        return self.screen_height - 100

    def _calculate_pattern_widths(self):
        self.pattern_widths = {}
        for i, layer in enumerate(self.layers):
            layer_type = layer.get('type')
            if layer_type in ['rects', 'circles', 'polygons']:
                max_x = 0
                elements = layer.get('elements', [])
                if not elements:
                    self.pattern_widths[i] = self.screen_width
                    continue
                for element in elements:
                    if layer_type == 'rects':
                        if element[0] + element[2] > max_x: max_x = element[0] + element[2]
                    elif layer_type == 'circles':
                        if element[0] + element[2] > max_x: max_x = element[0] + element[2]
                    elif layer_type == 'polygons':
                        for point in element:
                            if point[0] > max_x: max_x = point[0]
                self.pattern_widths[i] = max_x if max_x > 0 else self.screen_width

    def draw(self, surface, scroll_x):
        for i, layer in enumerate(self.layers):
            layer_type = layer.get('type')
            color = layer.get('color', (0, 0, 0))
            speed = layer.get('speed', 1.0)
            layer_scroll = scroll_x * speed

            if layer_type == 'solid_color':
                surface.fill(color)
            elif layer_type == 'solid_rect':
                rect_data = layer.get('rect')
                pygame.draw.rect(surface, color, (0, rect_data[1], self.screen_width, self.screen_height - rect_data[1]))
            elif layer_type in ['rects', 'circles', 'polygons']:
                pattern_width = self.pattern_widths.get(i, self.screen_width)
                scroll_offset = layer_scroll % pattern_width
                
                # Si el color tiene alfa, preparamos una superficie temporal para toda la capa
                has_alpha = len(color) == 4
                target_surface = surface
                if has_alpha:
                    target_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)

                elements = layer.get('elements', [])
                for element_data in elements:
                    if layer_type == 'rects':
                        x_base, y, w, h = element_data
                        x_pos = x_base - scroll_offset
                        pygame.draw.rect(target_surface, color, (x_pos, y, w, h))
                        pygame.draw.rect(target_surface, color, (x_pos + pattern_width, y, w, h))

                    elif layer_type == 'circles':
                        cx_base, cy, r = element_data
                        cx_pos = cx_base - scroll_offset
                        pygame.draw.circle(target_surface, color, (int(cx_pos), int(cy)), int(r))
                        pygame.draw.circle(target_surface, color, (int(cx_pos + pattern_width), int(cy)), int(r))

                # Si usamos la superficie temporal, la bliteamos a la principal una sola vez
                if has_alpha:
                    surface.blit(target_surface, (0, 0))