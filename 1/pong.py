import pygame, math, sys, random, world
from collections import deque
import numpy as np
import imutils
import argparse
import cv2
import os

WIDTH = 1024
HEIGHT = 600
BACK = (0, 0, 0)
BORDER_MARGIN = 5
BORDER_COLOR = (250, 250, 250)
P_LENGTH = 100
P_WIDTH = 10
P_SPEED = 6
ME_COLOR = (255, 150, 150)
HIM_COLOR = (150, 150, 255)
ME_X = 20
HIM_X = WIDTH - ME_X
BALL_SPEED = 6
FPS = 60

# init ocv
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
LowerHsv = (151, 124, 107)
UpperHsv = (194, 201, 201)
LowerRgb = (0,22,146)
UpperRgb = (124,136,255)
pts = deque(maxlen=args["buffer"])

camera = cv2.VideoCapture(1)

# set pygames screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()

def processCamera():
	# grab the current frame
	(grabbed, frame) = camera.read()

	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=WIDTH, height=HEIGHT)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
	rgb = frame.copy()

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, LowerHsv, UpperHsv)
	mask = cv2.inRange(rgb, LowerRgb, UpperRgb)
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
		center = (WIDTH - center[0], center[1])
		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
            	# update the points queue

	# show the frame to our screen
	# cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF

	return center


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

def main():
	me_y = HEIGHT / 2 - P_LENGTH / 2
	him_y = HEIGHT / 2 - P_LENGTH / 2
	ball_p = (WIDTH / 2, HEIGHT / 2)
	ball_ang = random.random() * math.pi

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
			if event.type == pygame.QUIT:
				playing = False

		# calc
		my_location = processCamera()
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

if (__name__ == "__main__"):
	main()