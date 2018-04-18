

#!/usr/bin/python

import cv2
import numpy as np
import imutils
import pygame 
from pygame.locals import *
import RPi.GPIO as GPIO
#from gpiozero import LED, Button
from time import sleep

#gpio parameters
buttonPin = 15
leftLedPin = 11
centerLedPin = 12
rightLedPin = 13

#state variables
done = False
finished = False
refresh = False

#zoom and pan parameters
zoomLevel = 1
offsetX = 0
offsetY = 0
dx = 0
dy = 0 

#define for mouse button
LEFTBUTTON = 1
MIDDLEBUTTON = 2
RIGHTBUTTON = 3
WHEELUP = 4
WHEELDOWN = 5

# image parameters
BRIGHTNESS = 1000
WIDTH = 3264
HEIGHT = 2448
SCREENW = 1280
SCREENH	= 768

def Capture2Cameras():
	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		sleep(0.1)
		#(grabbed1,frame1) = capture1.read()
	frame1 = frame0.copy()
	frame1 = imutils.rotate_bound(frame1, 90)
	frame0 = imutils.rotate_bound(frame0, 90)

	while not grabbed0 : #(grabbed1 and grabbed0) :
		sleep(0.25)
	return frame0, frame1 
	
def ProcessFrames2One( frame0 , frame1):
	
	stack = np.hstack([frame0, frame1])
	height, width, channel = stack.shape
	ratioStack = height / width
	return stack, height, width, ratioStack
	
def ButtonCB(channel): # call back when button pressed
	refresh = True

def InitGPIO():	#Set up and init GPIO
	GPIO.setmode(GPIO.BOARD) # use number on the board
	GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP )
	GPIO.setup(leftLedPin, GPIO.OUT)
	GPIO.setup(rightLedPin, GPIO.OUT)
	GPIO.setup(centerLedPin, GPIO.OUT)
	GPIO.add_event_detect(buttonPin, GPIO.FALLING, callback=ButtonCB, bouncetime=75)
	
def InitPygame():
	pygame.init()
	windowSurface = pygame.display.set_mode((SCREENW, SCREENH))#, pygame.NOFRAME | pygame.FULLSCREEN)
	pygame.mouse.set_pos([SCREENW/2,SCREENH/2])
	pygame.mouse.set_visible(0)	
	
if __name__ == '__main__':
    
	#Set up and init GPIO 
	InitGPIO()
	
	# pygame init
	InitPygame()
	
	# capture from 2 webcams 
	capture0 = cv2.VideoCapture(0)
	#capture1 = cv2.VideoCapture(1)
	#capture0.set(10, BRIGHTNESS)
	#capture1.set(10, BRIGHTNESS)
	capture0.set(cv2.CAP_PROP_FRAME_WIDTH , WIDTH)
	#capture1.set(3 , WIDTH)
	capture0.set(cv2.CAP_PROP_FRAME_HEIGHT  , HEIGHT)
	#capture1.set(4  , HEIGHT)

	while not finished:
		
		f0,f1 = Capture2Cameras()
		collage, height, width, ratioCollage = ProcessFrames2One( f0 , f1)
		refresh = False
		
		while not refresh and not finished:
			zoom = collage[0: int(height/zoomLevel), 0: int(width/zoomLevel)] # line collumn => Y X
			zoom = cv2.resize(zoom, ( SCREENW, int(ratioCollage * SCREENW)), cv2.INTER_LANCZOS4)
			
			b ,g ,r = cv2.split(zoom)
			zoomrgb = cv2.merge((r, g ,b ))

			img = pygame.image.frombuffer(zoomrgb.tostring(), zoomrgb.shape[1::-1],"RGB")
			windowSurface.blit(img, (0, 0))	
			pygame.display.flip()

			done = False
			refresh = False
			finished = False
			while not done and not refresh and not finished:

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						finished = True
						#sys.exit()
					elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == LEFTBUTTON or event.button == WHEELUP) :
						print ('zoom In')
						zoomLevel = min(zoomLevel+1,8)
						print(zoomLevel)
						done = True
					elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == RIGHTBUTTON or event.button == WHEELDOWN) :
						print ('zoom Out')
						zoomLevel = max(zoomLevel-1,1)
						print(zoomLevel)
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_SPACE: 
						print('space')
						refresh = True
					elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
						print('escape')
						finished = True
					elif event.type == pygame.KEYDOWN and event.key == K_UP:
						dy = 100
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_DOWN:
						dy = -100
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_LEFT:
						dx = -100
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_RIGHT:
						dx = 100
						done = True
					elif event.type == pygame.MOUSEMOTION :
						(x,y) = event.pos
						dx =  x - SCREENW/2
						dy =  y - SCREENH/2
						#pygame.mouse.set_pos([600,400])
						print(dx)
						print(dy)
						done = True
				k = cv2.waitKey(25) & 0xFF



	print('exit')
	capture0.release()
	#capture1.release()
	cv2.destroyAllWindows()