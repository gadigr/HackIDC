import pygame, math, sys, random, world
from pygame.locals import *

WIDTH = 1024
HEIGHT = 600
BACK = (0, 0, 0)
P_LENGTH = 70
P_WIDTH = 10
P_SPEED = 2
ME_COLOR = (255, 150, 150)
HIM_COLOR = (150, 150, 255)
ME_X = 20
HIM_X = WIDTH - ME_X
BALL_SPEED = 2
FPS = 60

# set pygames screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()

def handle_ball(ball_p, ball_ang, me_y, him_y):
	dx = math.cos(ball_ang) * BALL_SPEED
	dy = math.sin(ball_ang) * BALL_SPEED
	new_x = ball_p[0] + dx
	new_y = ball_p[1] + dy
	
	if (new_x <= 0 or new_x >= WIDTH):
		#dx = -dx
		return
	if (new_y <= 0 or new_y >= HEIGHT):
		dy = -dy
	if (new_x >= ME_X and new_x <= ME_X + P_WIDTH and new_y >= me_y and new_y <= me_y + P_LENGTH):
		dx = -dx
	if (new_x >= HIM_X and new_x <= HIM_X + P_WIDTH and new_y >= him_y and new_y <= him_y + P_LENGTH):
		dx = -dx
	
	ball_p = (new_x, new_y)
	ball_ang = math.atan2(dy, dx)
	
	return ball_p, ball_ang

def ai(ball_p, ball_ang, him_y):
	y = him_y + P_LENGTH / 2
	if (y < ball_p[1]): him_y += P_SPEED
	else: him_y -= P_SPEED
	return him_y
	
def main():
	me_y = HEIGHT / 2 - P_LENGTH / 2
	him_y = HEIGHT / 2 - P_LENGTH / 2
	ball_p = (WIDTH / 2, HEIGHT / 2)
	ball_ang = random.random() * math.pi

	playing = True

	while playing:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				playing = False

		# calc
		me_y = pygame.mouse.get_pos()[1]
		him_y = ai(ball_p, ball_ang, him_y)
		ball_data = handle_ball(ball_p, ball_ang, me_y, him_y)

		if ball_data is not None:
			ball_p, ball_ang = ball_data
		else:
			playing = False

		# clear screen
		screen.fill(BACK)

		# draw
		pygame.draw.rect(screen, ME_COLOR, (ME_X, me_y, P_WIDTH, P_LENGTH))
		pygame.draw.rect(screen, HIM_COLOR, (HIM_X, him_y, P_WIDTH, P_LENGTH))

		pygame.draw.circle(screen, (255, 255, 255), map(int, ball_p), 7, 0)

		# show
		pygame.display.flip()

		# tick
		clock.tick(FPS)
	
if (__name__ == "__main__"):
	main()