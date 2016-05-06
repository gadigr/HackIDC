import pygame, math, sys, random, world, pygame.gfxdraw, imutils
from pygame.locals import *

#import ocv stuff
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

#snake
WIDTH = 1024
HEIGHT = 600
BACK = (204, 255, 255)
FORE = (0, 255, 0)
FOOD = (255, 102, 0)
HEAD_RADIUS = 10
TAIL_RADIUS = 1
MIN_COLLIDE_RADIUS = 50
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

#pong
BORDER_MARGIN = 5
BORDER_COLOR = (250, 250, 250)
P_LENGTH = 100
P_WIDTH = 10
P_SPEED = 6
ME_COLOR = (255, 150, 150)
HIM_COLOR = (150, 150, 255)
ME_X = 20
HIM_X = WIDTH - ME_X
BALL_SPEED = 8
FPS = 60

offset = (0,0)

ap = argparse.ArgumentParser()
ap.add_argument("-m", "--mouse",
	help="to position with mouse", required=False, action='store_true')
args = vars(ap.parse_args())



# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
LowerHsv = (0, 161, 121)
UpperHsv = (255, 243, 182)
#LowerHsv = (0, 100, 105)
#UpperHsv = (201, 253, 219)
LowerRgb = (0,22,146)
UpperRgb = (124,136,255)

camera = cv2.VideoCapture(0)

def processCamera():
	# grab the current frame
	(grabbed, frame) = camera.read()
	
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=WIDTH, height=HEIGHT)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
#	rgb = frame.copy()
	
	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, LowerHsv, UpperHsv)
#	mask = cv2.inRange(rgb, LowerRgb, UpperRgb)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = (0,0)

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
		c = max(cnts, key=cv2.contourArea)
		((x, y), radius) = cv2.minEnclosingCircle(c)
		M = cv2.moments(c)
		center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
		#center = (WIDTH - center[0], center[1])
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
            	# update the points queue

	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	return center

get_pos = pygame.mouse.get_pos if bool(args['mouse']) else processCamera

def init():
    done = False
    global offset
    
    while not done:
        screen.fill(BACK)
        

        #pos = processCamera()
        pos = get_pos()
        pos = (pos[0] + offset[0], pos[1] + offset[1])
        pygame.draw.circle(screen, FOOD, (WIDTH / 2, HEIGHT / 2), 30, 1)
        pygame.draw.circle(screen, FORE, pos, 10, 0)
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    # break # break out of the for loop
                elif event.key == pygame.K_SPACE:
					pos = get_pos()
					offset = (WIDTH / 2 - pos[0], HEIGHT / 2 - pos[1])
					# print offset

            elif event.type == pygame.QUIT:
                done = True
                # break # break out of the for loop	
         
        pygame.display.flip()
 
def handle_ball(ball_p, ball_ang, me_y, him_y, sound):
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
		sound.play()
	if (new_x >= HIM_X and new_x <= HIM_X + P_WIDTH and new_y >= him_y and new_y <= him_y + P_LENGTH):
		dx = -dx
		sound.play()
	
	ball_p = (new_x, new_y)
	ball_ang = math.atan2(dy, dx)
	
	return ball_p, ball_ang

def ai(ball_p, ball_ang, him_y):
	y = him_y + P_LENGTH / 2
	if (y < ball_p[1]): him_y += P_SPEED
	else: him_y -= P_SPEED
	return him_y

def make_rainbow_color():
	make_rainbow_color.counter += 1
	center = 128
	width = 127
	frequency = math.pi * 2 / 120
	red = math.sin(frequency * make_rainbow_color.counter  + 2) * width + center
	green = math.sin(frequency * make_rainbow_color.counter  + 0) * width + center
	blue = math.sin(frequency * make_rainbow_color.counter  + 4) * width + center

	return (red, green, blue)
make_rainbow_color.counter = 0

def pong_main():
	me_y = HEIGHT / 2 - P_LENGTH / 2
	him_y = HEIGHT / 2 - P_LENGTH / 2
	ball_p = (WIDTH / 2, HEIGHT / 2)
	ball_ang = random.random() * math.pi / 2 + 3 * math.pi / 4

	# background
	bg = pygame.image.load("images/pong-back.jpg").convert()

	# music
	boing_sound = pygame.mixer.Sound("music/boing.ogg")
	pygame.mixer.music.load("music/background.ogg")
	pygame.mixer.music.set_endevent(pygame.constants.USEREVENT)
	pygame.mixer.music.play(-1)

	# text
	font = pygame.font.SysFont("Tahoma", 40, False, False)

	playing = True

	while playing:
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					playing = True
					# break # break out of the for loop
			elif event.type == pygame.QUIT:
				playing = False

		# calc
		my_location = get_pos()
		me_y = pygame.mouse.get_pos()[1]
		him_y = ai(ball_p, ball_ang, him_y)
		ball_data = handle_ball(ball_p, ball_ang, my_location[1], him_y, boing_sound)

		if ball_data is not None:
			ball_p, ball_ang = ball_data
		else:
			playing = False

		# clear screen
		# screen.fill(BACK)
		screen.blit(bg, (0,0))
		text = font.render("DRONE PONG", True, make_rainbow_color())
		screen.blit(text, ((WIDTH / 2) - 135, BORDER_MARGIN + 20))

		# draw borders
		pygame.draw.rect(screen, BORDER_COLOR, (BORDER_MARGIN, BORDER_MARGIN, WIDTH - (BORDER_MARGIN * 2), HEIGHT - (BORDER_MARGIN * 2)), 3)
		pygame.draw.rect(screen, BORDER_COLOR, (WIDTH / 2, BORDER_MARGIN, 3, HEIGHT - BORDER_MARGIN * 2))

		# draw players and ball
		pygame.draw.rect(screen, ME_COLOR, (ME_X, my_location[1], P_WIDTH, P_LENGTH))
		pygame.draw.rect(screen, HIM_COLOR, (HIM_X, him_y, P_WIDTH, P_LENGTH))
		pygame.draw.circle(screen, (255, 255, 255), map(int, ball_p), 8, 0)
		pygame.draw.circle(screen, (255, 0, 0), my_location, 10, 0)

		# show
		pygame.display.flip()

		# tick
		clock.tick(FPS)

	screen.fill((0, 0, 0))
	text = font.render("YOU LOST", True, (255, 0, 0))
	screen.blit(text, ((WIDTH / 2) - 135, BORDER_MARGIN + 20))
	pygame.display.flip()

	# cleanup the camera and close any open windows
	camera.release()
	cv2.destroyAllWindows() 

def mainGame():
	done = False
	global offset
	my_world = world.world(30, make_food())
	MUSIC.play()
	while not done:

		clock.tick(30)
		screen.blit(BACK_IMG, (0, 0))
		for event in pygame.event.get():
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					done = True
					# break # break out of the for loop
			elif event.type == pygame.QUIT:
				done = True
				# break # break out of the for loop
	

		#pos = processCamera()
		pos = get_pos()
		pos = (pos[0] + offset[0], pos[1] + offset[1])

		# my_world.positions.append(pygame.mouse.get_pos())
		my_world.positions.append(pos)
		my_world.positions = my_world.positions[-my_world.length:]

		if (len(my_world.positions) > 1):
			pygame.gfxdraw.filled_polygon(screen, create_poly(my_world.positions), FORE)

		handle_food(my_world)
		if (my_world.length < my_world.new_length):
			my_world.length += 1

		screen.blit(BIRD_IMG, map(lambda n: n - FOOD_SIZE / 2, my_world.food))
		pygame.display.flip()

def make_food():
	return (random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50))
	
def create_poly(positions):
	poly = [positions[0]]
	length = len(positions)
	
	for i in range(length - 1):
		radius = int(HEAD_RADIUS * float(i) / length + TAIL_RADIUS * float(length - i) / length)
		alpha = math.atan2(positions[i + 1][1] - positions[i][1], positions[i + 1][0] - positions[i][0])
		beta = alpha + math.pi / 2
		gamma = alpha - math.pi / 2

		x, y = positions[i]
		left = (x + math.cos(beta) * radius, y + math.sin(beta) * radius)
		right = (x + math.cos(gamma) * radius, y + math.sin(gamma) * radius)
		poly.append(right)
		poly.insert(0, left)
		
	poly.append(positions[length - 1])
	
	return (poly)
	
def handle_food(world):
	if (dist(world.food, world.positions[len(world.positions) - 1]) < MIN_COLLIDE_RADIUS):

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
	init()
	pong_main()
	mainGame()
	
	
if (__name__ == "__main__"):
	main()