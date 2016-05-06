import pygame, math, sys
from pygame.locals import *
WIDTH = 1024
HEIGHT = 768
BACK = (204, 255, 255)
FORE = (0, 255, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()

while True:
	screen.fill(BACK)
	pygame.event.get()
	pygame.draw.circle(screen, FORE, pygame.mouse.get_pos(), 10, 0)
	pygame.display.flip()