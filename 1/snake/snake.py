import pygame, math, sys, random, world, pygame.gfxdraw, imutils
from pygame.locals import *
WIDTH = 1024
HEIGHT = 600
BACK = (204, 255, 255)
FORE = (0, 255, 0)
FOOD = (255, 102, 0)
HEAD_RADIUS = 10
TAIL_RADIUS = 1
MIN_COLLIDE_RADIUS = 25
FOOD_SIZE = 50
BACK_IMG = pygame.transform.scale(pygame.image.load(r'assets\background.png'), (WIDTH, HEIGHT))
BIRD_IMG = pygame.transform.scale(pygame.image.load(r'assets\bird.png'), (FOOD_SIZE, FOOD_SIZE))
GROWTH_RATE = 1.25
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()
pygame.mixer.init(44100, -16, 2, 2048)
MUSIC = pygame.mixer.Sound(r'assets\banjo.ogg')
EAT = pygame.mixer.Sound(r'assets\Eat.ogg')

def mainGame():
	my_world = world.world(30, make_food())
	MUSIC.play()
	while True:
		#screen.fill(BACK)
		clock.tick(30)
		screen.blit(BACK_IMG, (0, 0))
		pygame.event.get()
		my_world.positions.append(pygame.mouse.get_pos())
		my_world.positions = my_world.positions[-my_world.length:]
		#if (check_collision(my_world.positions)):
		#	return
		if (len(my_world.positions) > 1):
			pygame.gfxdraw.filled_polygon(screen, create_poly(my_world.positions), FORE)
			#pygame.gfxdraw.bezier(screen, create_poly(my_world.positions), 2, FORE)
			#pygame.draw.polygon(screen, FORE, create_poly(my_world.positions), 0)
			#pygame.draw.aalines(screen, FORE, True, create_poly(my_world.positions))
		#else:
			
		#for i in range(len(my_world.positions)):
			#p = my_world.positions[i]
			#radius = int(HEAD_RADIUS * float(i) / my_world.length + TAIL_RADIUS * float(my_world.length - i) / my_world.length)
			#pygame.draw.circle(screen, FORE, p, radius, 0)
		handle_food(my_world)
		if (my_world.length < my_world.new_length):
			my_world.length += 1
		#pygame.draw.circle(screen, FOOD, my_world.food, 8, 0)
		screen.blit(BIRD_IMG, map(lambda n: n - FOOD_SIZE / 2, my_world.food))
		pygame.display.flip()

def make_food():
	return (random.randint(10, WIDTH - 10), random.randint(10, HEIGHT - 10))
	
def create_poly(positions):
	poly = [positions[0]]
	length = len(positions)
	
	for i in range(length - 1):
		radius = int(HEAD_RADIUS * float(i) / length + TAIL_RADIUS * float(length - i) / length)
		alpha = math.atan2(positions[i + 1][1] - positions[i][1], positions[i + 1][0] - positions[i][0])
		beta = alpha + math.pi / 2
		gamma = alpha - math.pi / 2
		#x, y = (positions[i][0] + positions[i + 1][0]) / 2, (positions[i][1] + positions[i + 1][0]) / 2
		x, y = positions[i]
		left = (x + math.cos(beta) * radius, y + math.sin(beta) * radius)
		right = (x + math.cos(gamma) * radius, y + math.sin(gamma) * radius)
		poly.append(right)
		poly.insert(0, left)
		
	poly.append(positions[length - 1])
	
	return (poly)
	
def handle_food(world):
	if (dist(world.food, world.positions[len(world.positions) - 1]) < MIN_COLLIDE_RADIUS):
		#world.new_length = int(world.length * GROWTH_RATE)
		world.new_length += 15
		world.food = make_food()
		EAT.play()
		
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