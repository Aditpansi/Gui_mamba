import pygame
import math
import serial
import time

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 400
PI = math.pi
RADAR_Y_OFFSET = 50
FPS = 60

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 50, 0, 76)

# Radar class
class Radar:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Azimuth-Elevation Radar")
        self.clock = pygame.time.Clock()
        self.sweep_angle = -110.0
        self.font = pygame.font.Font(pygame.font.match_font('arial'), 12)
        self.large_font = pygame.font.Font(pygame.font.match_font('arial'), 24)
        self.running = True

    def draw_radar_background(self):
        # Draw radar semi-circle
        for i in range(221):
            angle = (i - 110) * PI / 180.0 + PI / 2.0
            x = math.cos(angle) * WINDOW_HEIGHT / 2.0
            y = -math.sin(angle) * WINDOW_HEIGHT / 2.0
            pygame.draw.aalines(self.screen, DARK_GREEN, False, [
                (WINDOW_WIDTH / 2 + x, WINDOW_HEIGHT / 2 + RADAR_Y_OFFSET + y)
            ])
        
        # Outline
        pygame.draw.arc(self.screen, GREEN, 
                (WINDOW_WIDTH / 2 - WINDOW_HEIGHT / 2, RADAR_Y_OFFSET, 
                 WINDOW_HEIGHT, WINDOW_HEIGHT), 
                math.radians(-110), math.radians(110), 2)
