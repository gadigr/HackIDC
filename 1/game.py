import pygame, math, sys, random, world
from pygame.locals import *

#import ocv stuff
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

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
offset = (0,0)

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

camera = cv2.VideoCapture(0)

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

def init():
    done = False
    global offset
    
    while not done:
        screen.fill(BACK)
        pygame.event.get()

        pos = processCamera()
        pos = (pos[0] + offset[0], pos[1] + offset[1])
        pygame.draw.circle(screen, FOOD, (WIDTH / 2, HEIGHT / 2), 30, 1)
        pygame.draw.circle(screen, FORE, pos, 10, 0)
        
#        pressed = pygame.key.get_pressed()
#        print pressed
#        if pressed[pygame.K_ESCAPE]:
##            done = True
#            break
#        if pressed[pygame.K_w]:
##            offset = (WIDTH / 2 - pos[0], HEIGHT / 2 - pos[1])
#            print offset
#            break
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    break # break out of the for loop
                elif event.key == pygame.K_SPACE:
                    offset = (WIDTH / 2 - pos[0], HEIGHT / 2 - pos[1])
                    print offset
                    break
            elif event.type == pygame.QUIT:
                done = True
                break # break out of the for loop

                #   offset 
        if done:
            break # to break out of the while loop		
         
        pygame.display.flip()
        

def mainGame():
	#positions = []
	#food = None
	done = False	
	#length = 200

	my_world = world.world(50, make_food())
	while not done:
        
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
            
		screen.fill(BACK)
		pygame.event.get()
		my_world.positions.append(processCamera())
		my_world.positions = my_world.positions[-my_world.length:]
		#if (check_collision(my_world.positions)):
			#return
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
    init()
    mainGame()
	
	
if (__name__ == "__main__"):
	main()