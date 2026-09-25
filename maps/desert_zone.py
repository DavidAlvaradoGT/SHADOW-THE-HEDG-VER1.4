# maps/desert_zone.py
import pygame

class DesertZone:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.name = "desert_zone"

        self.level_data = {
            "layers": [
                {"type": "solid_color", "color": (240, 230, 140)},
                {"type": "circles", "color": (255, 215, 0), "speed": 0.05, "elements": [[1000, 100, 80]]},
                {
                    "type": "polygons", "color": (210, 180, 140), "speed": 0.15,
                    "elements": [
                        [[200, 500], [400, 200], [600, 500]],
                        [[800, 500], [950, 250], [1100, 500]],
                    ]
                },
                {
                    "type": "rects", "color": (210, 180, 140), "speed": 0.3,
                    "elements": [[50, 350, 400, 150], [500, 300, 350, 200], [900, 380, 300, 120]],
                },
                {
                    "type": "rects", "color": (0, 100, 0), "speed": 0.8,
                    "elements": [
                        [150, 420, 15, 80], [145, 440, 25, 10],
                        [700, 450, 20, 50], [690, 460, 40, 10],
                        [1100, 400, 18, 100], [1092, 420, 34, 12],
                    ]
                },
                {"type": "solid_rect", "color": (194, 178, 128), "speed": 1.0, "rect": [0, 500, 1280, 220]},
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
                elements = layer.get('elements', [])
                for element_data in elements:
                    if layer_type == 'rects':
                        x_base, y, w, h = element_data
                        x_pos = x_base - scroll_offset
                        pygame.draw.rect(surface, color, (x_pos, y, w, h))
                        pygame.draw.rect(surface, color, (x_pos + pattern_width, y, w, h))
                    elif layer_type == 'circles':
                        cx_base, cy, r = element_data
                        cx_pos = cx_base - scroll_offset
                        pygame.draw.circle(surface, color, (int(cx_pos), int(cy)), int(r))
                        pygame.draw.circle(surface, color, (int(cx_pos + pattern_width), int(cy)), int(r))
                    elif layer_type == 'polygons':
                        points = [(p[0] - scroll_offset, p[1]) for p in element_data]
                        pygame.draw.polygon(surface, color, points)
                        points_copy = [(p[0] + pattern_width, p[1]) for p in points]
                        pygame.draw.polygon(surface, color, points_copy)