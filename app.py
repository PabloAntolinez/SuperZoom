

#!/usr/bin/python

import cv2
import numpy as np
import time
import matplotlib
import imutils
#matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
import pygame #voor beeld en geluid
from pygame.locals import *


done = False
finished = False
refresh = False
zoomLevel = 1
offsetX = 0
offsetY = 0

dx = 0
dy = 0 

LEFTBUTTON = 1
MIDDLEBUTTON = 2
RIGHTBUTTON = 3

BRIGHTNESS = 1000
WIDTH = 3264
HEIGHT = 2448
SCREENW = 1920
SCREENH	= 1080

		
if __name__ == '__main__':
    
	pygame.init()
	capture0 = cv2.VideoCapture(0)
	#capture1 = cv2.VideoCapture(1)
	#capture0.set(10, BRIGHTNESS)
	#capture1.set(10, BRIGHTNESS)
	capture0.set(cv2.CAP_PROP_FRAME_WIDTH , WIDTH)
	#capture1.set(3 , WIDTH)
	capture0.set(cv2.CAP_PROP_FRAME_HEIGHT  , HEIGHT)
	#capture1.set(4  , HEIGHT)
		
	windowSurface = pygame.display.set_mode((SCREENW, SCREENH), pygame.NOFRAME | pygame.FULLSCREEN)
	pygame.mouse.set_pos([SCREENW/2,SCREENH/2])
	pygame.mouse.set_visible(0)
	
	myfont = pygame.font.SysFont("monospace", 15)
	
	while not finished:
		for g in range(5): # because stupid videostream contains 5 images and cannot reduce 
			(grabbed0,frame0) = capture0.read()
			time.sleep(0.1)
		#(grabbed1,frame1) = capture1.read()
		frame1 = frame0.copy()
		frame1 = imutils.rotate_bound(frame1, 90)
		frame0 = imutils.rotate_bound(frame0, 90)
		#cv2.imshow('frame1', frame1)
		while not grabbed0 : #(grabbed1 and grabbed0) :
			time.sleep(0.25)

				
		#f0 = cv2.resize(frame0, (400,300), cv2.INTER_LANCZOS4).copy()
		#f1 = cv2.resize(frame1, (WIDTH,HEIGHT), cv2.INTER_LANCZOS4).copy()
		
		
		#cv2.imshow('f1', f1)
		collage = np.hstack([frame0, frame1])

		
		height, width, channel = collage.shape
		ratioCollage = height / width
		refresh = False
		while not refresh and not finished:
			zoom = collage[0: int(height/zoomLevel), 0: int(width/zoomLevel)] # line collumn => Y X
			zoom = cv2.resize(zoom, ( SCREENW, int(ratioCollage * SCREENW)), cv2.INTER_LANCZOS4)
			
			b ,g ,r = cv2.split(zoom)
			zoomrgb = cv2.merge((r, g ,b ))

			img = pygame.image.frombuffer(zoomrgb.tostring(), zoomrgb.shape[1::-1],"RGB")
			
			text = str(dx) + ' ' + str(dy)
			#pygame.freetype.Font.render_to(windowSurface, (10,10), text, (255,255,255))
			
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
					elif event.type == pygame.MOUSEBUTTONDOWN and event.button == LEFTBUTTON :
						print ('zoom In')
						zoomLevel = min(zoomLevel+1,8)
						print(zoomLevel)
						done = True
					elif event.type == pygame.MOUSEBUTTONDOWN and event.button == RIGHTBUTTON :
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