#import pygame stuuf
import pygame, math, sys
from pygame.locals import *

#import ocv stuff
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

# init pygame 
WIDTH = 1024
HEIGHT = 768
BACK = (204, 255, 255)
FORE = (0, 255, 0)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.init()
done = False

# init ocv 
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
pts = deque(maxlen=args["buffer"])

camera = cv2.VideoCapture(0)

def processCamera():
	# grab the current frame
	(grabbed, frame) = camera.read()
	
	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "green", then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, greenLower, greenUpper)
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

		# only proceed if the radius meets a minimum size
		if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
			cv2.circle(frame, (int(x), int(y)), int(radius),
				(0, 255, 255), 2)
			cv2.circle(frame, center, 5, (0, 0, 255), -1)
            	# update the points queue

	# show the frame to our screen
	#cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
	
	return center

#game loop
while not done:
	######################## CHECK INPUT
	for event in pygame.event.get():
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				done = True
				break # break out of the for loop
		elif event.type == pygame.QUIT:
			done = True
			break # break out of the for loop
	if done:
		break # to break out of the while loop
	
	####################### PROCESS
	pos = processCamera()

	####################### DRAW	
	screen.fill(BACK)
	pygame.event.get()
	#pygame.draw.circle(screen, FORE, pygame.mouse.get_pos(), 10, 0)
	print pos
	pygame.draw.circle(screen, FORE, pos, 10, 0)
	pygame.display.flip()

	