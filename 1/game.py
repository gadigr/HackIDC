import pygame, math, sys, random, world
from pygame.locals import *
WIDTH = 1024
HEIGHT = 600
BACK = (204, 255, 255)
FORE = (0, 255, 0)
FOOD = (255, 102, 0)
HEAD_RADIUS = 10
TAIL_RADIUS = 1
MIN_COLLIDE_RADIUS = 25
GROWTH_RATE = 1.25
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()

def mainGame():
	#positions = []
	#food = None
	#length = 200
	my_world = world.world(50, make_food())
	while True:
		screen.fill(BACK)
		pygame.event.get()
		my_world.positions.append(pygame.mouse.get_pos())
		my_world.positions = my_world.positions[-my_world.length:]
		if (check_collision(my_world.positions)):
			return
		for i in range(len(my_world.positions)):
			p = my_world.positions[i]
			radius = int(HEAD_RADIUS * float(i) / my_world.length + TAIL_RADIUS * float(my_world.length - i) / my_world.length)
			pygame.draw.circle(screen, FORE, p, radius, 0)
		handle_food(my_world)
		if (my_world.length < my_world.new_length):
			my_world.length += 1
		pygame.draw.circle(screen, FOOD, my_world.food, 8, 0)
		pygame.display.flip()

def make_food():
	return (random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10))
		
def handle_food(world):
	if (dist(world.food, world.positions[len(world.positions) - 1]) < MIN_COLLIDE_RADIUS):
		world.new_length = int(world.length * GROWTH_RATE)
		world.food = make_food()
		
def dist(p1, p2):
	return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))
		
def check_collision(positions):
	head = positions[-1:][0]
	positions = positions[:-1]
	prev_p = head
	tot_dist = 0
	for i in range(len(positions) - 1, 0, -1):
		curr_p = positions[i]
		tot_dist += dist(curr_p, prev_p)
		if (dist(head, curr_p) < 1.5 and tot_dist >= MIN_COLLIDE_RADIUS):
			return True
		
		prev_p = curr_p
	
	return False
		
def main():
	mainGame()
	
	
if (__name__ == "__main__"):
	main()