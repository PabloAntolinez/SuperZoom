

#!/usr/bin/python

import cv2
import numpy as np
import imutils
import pygame 
from pygame.locals import *
import RPi.GPIO as GPIO
#from gpiozero import LED, Button
from time import sleep
from time import time
import subprocess


#gpio parameters
buttonPin = 37
leftLedPin = 7
centerLedPin = 5
rightLedPin = 3
offButtonPin = 33
onLedPin = 29
holdTimeOff = 5


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
CAMW = 3264
CAMH = 2448
SCREENW = 1280  #1920
SCREENH	= 768   #1080
IMTOTW=5803
IMTOTH=3264
NB_IM_AVG = 3

windowSurface = None

def ProcessFrames2One():
    # Allocate empty Array for averaging
	meanStack = np.empty((5, 1944, 2592, 3), dtype=np.uint8)
	# ON Left LED
	GPIO.output(leftLedPin , GPIO.HIGH)  
	GPIO.output(centerLedPin , GPIO.LOW)
	GPIO.output(rightLedPin , GPIO.LOW)

	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		while not grabbed0 : 
			sleep(0.15)

	for g in range(NB_IM_AVG): # average of 5 images
		(grabbed0,meanStack[g,:,:,:]) = capture0.read()
		while not grabbed0 : 
			sleep(0.1)		
	mean= np.mean(meanStack, axis=0)

	bufferLeft = np.array(np.round(mean), dtype=np.uint8)

	##ON Center LED
	GPIO.output(leftLedPin , GPIO.LOW) 
	GPIO.output(centerLedPin , GPIO.HIGH)
	GPIO.output(rightLedPin , GPIO.LOW)
	
	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		while not grabbed0 : 
			sleep(0.15)

	for g in range(NB_IM_AVG): # average of 5 images
		(grabbed0,meanStack[g,:,:,:]) = capture0.read()
		while not grabbed0 : 
			sleep(0.1)		
	mean= np.mean(meanStack, axis=0)

	bufferLeft2 = np.array(np.round(mean), dtype=np.uint8)
	
	bufferLeft=np.minimum(bufferLeft,bufferLeft2)
	
	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		while not grabbed0 : 
			sleep(0.15)

	for g in range(NB_IM_AVG): # average of 5 images
		(grabbed0,meanStack[g,:,:,:]) = capture0.read()
		while not grabbed0 : 
			sleep(0.1)		
	mean= np.mean(meanStack, axis=0)

	bufferRight2 = np.array(np.round(mean), dtype=np.uint8)

	#ON Right LED
	GPIO.output(leftLedPin , GPIO.LOW) 
	GPIO.output(centerLedPin , GPIO.LOW)
	GPIO.output(rightLedPin , GPIO.HIGH)

	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		while not grabbed0 : 
			sleep(0.15)

	for g in range(NB_IM_AVG): # average of 5 images
		(grabbed0,meanStack[g,:,:,:]) = capture0.read()
		while not grabbed0 : 
			sleep(0.1)		
	mean= np.mean(meanStack, axis=0)

	bufferRight = np.array(np.round(mean), dtype=np.uint8)
	
	bufferRight=np.minimum(bufferRight,bufferRight2)

	#ON Center LED   on rallume le centre
	GPIO.output(leftLedPin , GPIO.LOW) 
	GPIO.output(centerLedPin , GPIO.LOW)
	GPIO.output(rightLedPin , GPIO.LOW)
	
	bufferLeft = imutils.rotate_bound(bufferLeft, 270)
	bufferRight = imutils.rotate_bound(bufferRight, 270)
	
	#Collage et rajoute des bandes NOIRES laterales
	emptyBand = np.zeros((2592 , 454, 3), dtype=np.uint8)
	stack = np.hstack([emptyBand, bufferLeft, bufferRight,emptyBand])
	height, width, channel = stack.shape
	ratioStack = height / width
	return stack, height, width, ratioStack
	
def ButtonCB(channel): # call back when button pressed
	global refresh
	refresh = True
	
def OffCB(channel): # call back when button pressed
	startTime = time()	
	while GPIO.input(offButtonPin) == 0 : # wait for release
		pass		
	holdTime = time() - startTime
	
	if holdTime > holdTimeOff :
		print("off")
		# subprocess.call(['shutdown', '-h', 'now'], shell=False)

def InitGPIO():	#Set up and init GPIO
	GPIO.setmode(GPIO.BOARD) # use number on the board
	GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP )
	GPIO.setup(offButtonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP )	
	GPIO.setup(leftLedPin, GPIO.OUT)
	GPIO.setup(rightLedPin, GPIO.OUT)
	GPIO.setup(centerLedPin, GPIO.OUT)
	GPIO.setup(onLedPin, GPIO.OUT)
	GPIO.add_event_detect(buttonPin, GPIO.FALLING, callback=ButtonCB, bouncetime=75)
	GPIO.add_event_detect(offButtonPin, GPIO.FALLING, callback=OffCB, bouncetime=500)
	GPIO.output(onLedPin , GPIO.HIGH)
	
def InitPygame():
	global windowSurface
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
	### dict of the settings 

	# qui marche:
	# cam_props = {'brightness': 0, 'contrast': 32, 'saturation': 105, 'hue': 0,
             # 'white_balance_temperature_auto': 1, 'white_balance_temperature': 4600, 'gamma': 100 ,'gain': 0,
             # 'sharpness': 3, 'backlight_compensation': 1 ,'exposure_auto': 3,
             # 'exposure_absolute': 93, 'exposure_auto_priority': 1  }

	# en test
	# cam_props = {'brightness': 0, 'contrast': 22, 'saturation': 100, 'hue': 0,
             # 'white_balance_temperature_auto': 0, 'white_balance_temperature': 4500, 'gamma': 92 ,'gain': 20,
             # 'sharpness': 0, 'backlight_compensation': 0 ,'exposure_auto': 3,
             # 'exposure_absolute': 100, 'exposure_auto_priority': 1  }


	### go through and set each property; 
	# for key in cam_props:
	    # subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format(key, str(cam_props[key]))],shell=True)

	### uncomment to print out/verify the above settings took
	# subprocess.call(['v4l2-ctl -d /dev/video0 -l'], shell=True)
  
	### showing that I *think* one should only create the opencv capture object after these are set
	### also remember to change the device number if necessary
	capture0 = cv2.VideoCapture(0)
	capture0.set(cv2.CAP_PROP_FRAME_WIDTH , CAMW)
	capture0.set(cv2.CAP_PROP_FRAME_HEIGHT , CAMH)

	while not finished:
		
		#f0,f1 = Capture2Cameras()
		collage, height, width, ratioCollage = ProcessFrames2One()
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