import pygame, math, sys
from pygame.locals import *
WIDTH = 1024
HEIGHT = 768
BACK = (204, 255, 255)
FORE = (0, 255, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()
positions = []

while True:
	screen.fill(BACK)
	pygame.event.get()
	positions.append(pygame.mouse.get_pos())
	for p in positions:
		pygame.draw.circle(screen, FORE, p, 10, 0)
	pygame.display.flip()