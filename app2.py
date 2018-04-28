import cv2
import numpy as np
import imutils
import pygame 
from pygame.locals import *
import RPi.GPIO as GPIO
#from gpiozero import LED, Button
from time import sleep
import subprocess
import time

#gpio parameters
buttonPin = 37
leftLedPin = 7
centerLedPin = 5
rightLedPin = 3

#state variables
done = False
finished = False
reAcquire = True

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
#SCREENW = 1920 #1280  #1920
#SCREENH	= 1080 #768   #1080
SCREENW = 1280  #1920
SCREENH	= 768   #1080
BANDENOIRWIDTH=454
IMTOTW=BANDENOIRWIDTH*2+CAMH*2
IMTOTH=CAMW
INDEXRIGHTCAM=0
INDEXLEFTCAM=1
NBFRAMEAVERAGE=1

timeStampButton=time.time()
windowSurface = None

def SingleLightAcq():

	global collage
	
	(grabbed0,bufferLeft) = capture0.read()
	while not grabbed0 : 
		sleep(0.1)
		
	b ,g ,r = cv2.split(bufferLeft )    
	bufferLeft = cv2.merge((r, g ,b ))	
	bufferLeft = imutils.rotate_bound(bufferLeft, 270)
	
			#Collage et rajoute des bandes NOIRES laterales
	collage = np.hstack([np.zeros((CAMW , BANDENOIRWIDTH, 3), dtype=np.uint8), bufferLeft, np.zeros((CAMW , CAMH + BANDENOIRWIDTH, 3), dtype=np.uint8)])

def MultiLightAcq2():

	global collage
    # Allocate empty Array for averaging
	meanStack = np.empty((5, CAMH, CAMW, 3), dtype=np.uint8)
	# ON Left LED
	GPIO.output(leftLedPin , GPIO.HIGH)  
	GPIO.output(centerLedPin , GPIO.LOW)
	GPIO.output(rightLedPin , GPIO.LOW)

	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		while not grabbed0 : 
			sleep(0.15)

	for g in range(NBFRAMEAVERAGE): # average of 5 images
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

	for g in range(NBFRAMEAVERAGE): # average of 5 images
		(grabbed0,meanStack[g,:,:,:]) = capture0.read()
		while not grabbed0 : 
			sleep(0.1)		
	mean= np.mean(meanStack, axis=0)

	bufferLeft2 = np.array(np.round(mean), dtype=np.uint8)
	
	bufferLeft=np.minimum(bufferLeft,bufferLeft2)
	
	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture1.read()
		while not grabbed0 : 
			sleep(0.15)

	for g in range(NBFRAMEAVERAGE): # average of 5 images
		(grabbed0,meanStack[g,:,:,:]) = capture1.read()
		while not grabbed0 : 
			sleep(0.1)		
	mean= np.mean(meanStack, axis=0)

	bufferRight2 = np.array(np.round(mean), dtype=np.uint8)

	#ON Right LED
	GPIO.output(leftLedPin , GPIO.LOW) 
	GPIO.output(centerLedPin , GPIO.LOW)
	GPIO.output(rightLedPin , GPIO.HIGH)

	for g in range(6): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture1.read()
		while not grabbed0 : 
			sleep(0.15)

	for g in range(NBFRAMEAVERAGE): # average of 5 images
		(grabbed0,meanStack[g,:,:,:]) = capture1.read()
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
	emptyBand = np.zeros((CAMW , BANDENOIRWIDTH, 3), dtype=np.uint8)
	collage = np.hstack([emptyBand, bufferLeft, bufferRight,emptyBand])
	return 


def MultiLightAcq():  
		
	global collage
		
	# ON Left LED
	GPIO.output(leftLedPin , GPIO.HIGH)  
	GPIO.output(centerLedPin , GPIO.LOW)
	GPIO.output(rightLedPin , GPIO.LOW)                         # (4s)
	
	for g in range(5): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		#sleep(5)
		#(grabbed1,frame1) = capture1.read()
		
	while not grabbed0 : 
		sleep(0.1)
	# fin du vidage du stream camera
	
	bufferLeft = np.empty(( CAMH, CAMW, 3), dtype=np.float32) # creation du buffer FLOAT vide 
		
	for g in range(NBFRAMEAVERAGE): # somme les 5 images
		(grabbed0,frame0) = capture0.read()
		while not grabbed0 : 
			sleep(0.1)
		bufferLeft=bufferLeft+frame0.astype('float32') 
	bufferLeft=bufferLeft/NBFRAMEAVERAGE              # 1s     (13s)
	bufferLeft=bufferLeft.astype('uint8')              # redescendu a 11s !!!

	# ON Center LED
	GPIO.output(leftLedPin , GPIO.LOW) 
	GPIO.output(centerLedPin , GPIO.HIGH)
	GPIO.output(rightLedPin , GPIO.LOW)

	for g in range(5): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed0,frame0) = capture0.read()
		#sleep(5)
		#(grabbed1,frame1) = capture1.read()

	while not grabbed0 : # wait the end of the acquisitions
		sleep(0.1)
		
	bufferLeft2= np.empty(( CAMH, CAMW, 3), dtype=np.float32) # creation du buffer en FLOAT vide 

	for g in range(NBFRAMEAVERAGE): # somme les 5 images
		(grabbed0,frame0) = capture0.read()
		while not grabbed0 : 
			sleep(0.1)
		bufferLeft2=bufferLeft2+frame0.astype('float32') 
	bufferLeft2=bufferLeft2/NBFRAMEAVERAGE
	bufferLeft2=bufferLeft2.astype('uint8') 
	bufferLeft=np.minimum(bufferLeft,bufferLeft2)

	frame0 = bufferLeft

	# ON Center LED
	# it's still ON

	for g in range(5): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed1,frame1) = capture1.read()    # still 0 cause only one CAMERA !! 
		
	while not grabbed1 : # wait the end of the acquisitions
		sleep(0.1)
		
	bufferRight= np.empty(( CAMH, CAMW, 3), dtype=np.float32) # creation du buffer en FLOAT vide 

	for g in range(NBFRAMEAVERAGE): # somme les 5 images
		(grabbed1,frame1) = capture1.read()
		while not grabbed1 : 
			sleep(0.1)
		bufferRight=bufferRight+frame1.astype('float32') 
	bufferRight=bufferRight/NBFRAMEAVERAGE
	bufferRight=bufferRight.astype('uint8') 

	# ON Right LED
	GPIO.output(leftLedPin , GPIO.LOW) 
	GPIO.output(centerLedPin , GPIO.LOW)
	GPIO.output(rightLedPin , GPIO.HIGH)

	for g in range(5): # because stupid videostream contains 5 images and cannot reduce 
		(grabbed1,frame1) = capture1.read()

	while not grabbed1 : # wait the end of the acquisitions
		sleep(0.1)
		
	bufferRight2= np.empty(( CAMH, CAMW, 3), dtype=np.float32) # creation du buffer en FLOAT vide 

	for g in range(NBFRAMEAVERAGE): # somme les 5 images
		(grabbed1,frame1) = capture1.read()
		while not grabbed1 : 
			sleep(0.01)
		bufferRight2=bufferRight2+frame1.astype('float32') 
	bufferRight2=bufferRight2/NBFRAMEAVERAGE
	bufferRight2=bufferRight2.astype('uint8') 
	bufferRight=np.minimum(bufferRight,bufferRight2)

	# ON Center LED   on rallume le centre
	GPIO.output(leftLedPin , GPIO.LOW) 
	GPIO.output(centerLedPin , GPIO.HIGH)
	GPIO.output(rightLedPin , GPIO.LOW)

	bufferRight = imutils.rotate_bound(bufferRight, 270)
	bufferLeft = imutils.rotate_bound(bufferLeft, 270)
	
	#Collage et rajoute des bandes NOIRES laterales
	collage = np.hstack([np.zeros((CAMW , BANDENOIRWIDTH, 3), dtype=np.uint8), bufferLeft, bufferRight,np.zeros((CAMW , BANDENOIRWIDTH, 3), dtype=np.uint8)])
	b ,g ,r = cv2.split(collage )    #Attention Opération très lente pour rien ...
	collage = cv2.merge((r, g ,b ))

	height, width, channel = collage.shape
	print("Height= %d, Width= %d " % ( height , width ) )
	
	return 

def ButtonCB(channel): # call back when button pressed
	global reAcquire
	global multilight
	global askToToggleML
	global timeStampButton 
	print("Button pressed")
	
	duration =  time.time() - timeStampButton
	if duration > 3 :
	
		sleep(1.5)
		state = GPIO.input(buttonPin)  # read the bouton jaune state
		print("State of button is : %d" % state)
		if state == 0 :
			multilight = not multilight
			askToToggleML=1
			reAcquire = True
			print("Toggle single/mulit Light, multilight= %d" % multilight )
		else:	# dans ce cas on a relache le bouton rapidement
			if multilight==0:  # dans le cas du SingleLight on change l'etat des LED avec le bouton jaune
				if GPIO.input(centerLedPin) == 0:
					GPIO.output(leftLedPin , GPIO.HIGH) 
					GPIO.output(centerLedPin , GPIO.HIGH)
					GPIO.output(rightLedPin , GPIO.HIGH)
					print("SingleLight: swith on ")
				else:
					GPIO.output(leftLedPin , GPIO.LOW) 
					GPIO.output(centerLedPin , GPIO.LOW)
					GPIO.output(rightLedPin , GPIO.LOW)			
					print("SingleLight: swith OFF ")
				
		reAcquire = True
		
		timeStampButton=time.time()  # update the time stamp for next time
		
	else:
		print("Duration between 2 button.events is too small")

def InitGPIO():	#Set up and init GPIO
	GPIO.setmode(GPIO.BOARD) # use number on the board
	GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP )
	GPIO.setup(leftLedPin, GPIO.OUT)
	GPIO.setup(rightLedPin, GPIO.OUT)
	GPIO.setup(centerLedPin, GPIO.OUT)
	GPIO.add_event_detect(buttonPin, GPIO.FALLING, callback=ButtonCB, bouncetime=500)
	
def InitPygame():
	global windowSurface
	print("initPygame")
	pygame.init()
	windowSurface = pygame.display.set_mode((SCREENW, SCREENH))#, pygame.NOFRAME | pygame.FULLSCREEN)
	pygame.mouse.set_visible(1)
	pygame.mouse.set_pos([SCREENW/2,SCREENH/2])
	pygame.mouse.set_visible(0)	
	
if __name__ == '__main__':
    
	#Set up and init GPIO 
	InitGPIO()
	print("InitGPIO: done")
	GPIO.output(leftLedPin , GPIO.HIGH) 
	GPIO.output(centerLedPin , GPIO.HIGH)
	GPIO.output(rightLedPin , GPIO.HIGH)
	
	# init timestamp button 
	timeStampButton=time.time()
	
	# pygame init
	InitPygame()
	print("initPygame")   
	(x, y)=pygame.mouse.get_pos()
	print(x,y)
	print("InitPygame: done")

	# capture from 2 webcams 
	### dict of the settings 

	# qui marche:
	cam_props = {'brightness': 0, 'contrast': 32, 'saturation': 105, 'hue': 0,
             'white_balance_temperature_auto': 1, 'white_balance_temperature': 4600, 'gamma': 100 ,'gain': 0,
             'sharpness': 3, 'backlight_compensation': 1 ,'exposure_auto': 3,
             'exposure_absolute': 93, 'exposure_auto_priority': 1  }

	# en test
	cam_props = {'brightness': 0, 'contrast': 22, 'saturation': 100, 'hue': 0,
             'white_balance_temperature_auto': 0, 'white_balance_temperature': 4500, 'gamma': 92 ,'gain': 20,
             'sharpness': 0, 'backlight_compensation': 0 ,'exposure_auto': 3,
             'exposure_absolute': 100, 'exposure_auto_priority': 1  }


	### go through and set each property; 
	for key in cam_props:
	    subprocess.call(['v4l2-ctl -d /dev/video0 -c {}={}'.format(key, str(cam_props[key]))],shell=True)

	### uncomment to print out/verify the above settings took
	subprocess.call(['v4l2-ctl -d /dev/video0 -l'], shell=True)
	
 	### go through and set each property; 
	# for key in cam_props:
	    # subprocess.call(['v4l2-ctl -d /dev/video1 -c {}={}'.format(key, str(cam_props[key]))],shell=True)

	### uncomment to print out/verify the above settings took
	# subprocess.call(['v4l2-ctl -d /dev/video1 -l'], shell=True)
   
	### showing that I *think* one should only create the opencv capture object after these are set
	### also remember to change the device number if necessary
	capture0 = cv2.VideoCapture(INDEXLEFTCAM)
	capture0.set(cv2.CAP_PROP_FRAME_WIDTH , CAMW)
	capture0.set(cv2.CAP_PROP_FRAME_HEIGHT  , CAMH)
	

	### showing that I *think* one should only create the opencv capture object after these are set
	### also remember to change the device number if necessary
	# capture1 = cv2.VideoCapture(INDEXRIGHTCAM)
	# capture1.set(cv2.CAP_PROP_FRAME_WIDTH , CAMW)
	# capture1.set(cv2.CAP_PROP_FRAME_HEIGHT  , CAMH)
	
	collage = np.empty(( IMTOTH, IMTOTW, 3), dtype=np.uint8) # creation du buffer collage en UINT8 vide
	height, width, channel = collage.shape
	print("At init: Height= %d, Width= %d " % ( height , width ) )
	
	startX=100.0
	startY=100.0
	dx=0.0
	dy=0.0
	coeffSpeedMouse=7
	zoomLevel=2
	zoomIndex = int(0)
	zoomValues= [ SCREENH / CAMW , 0.4, 0.6, 0.8, 1, 1.25, 1.5, 1.75, 2, 3 , 3.5, 4]
	multilight=0

	while not finished:
		

		if multilight == 1 :
			print("Acquire new Multilight Image")
			MultiLightAcq2() #MultiLightAcq()  #collage est passe en global pour eviter une copie 
			reAcquire = False
			
			height, width, channel = collage.shape
			print("After new Acp : Height= %d, Width= %d " % ( height , width ) )
		else:  # single image
			SingleLightAcq()  #collage est passe en global pour eviter une copie
			reAcquire = False
			
		askToToggleML=0
		
		while not reAcquire and not finished:

			#print( "Update the position of image at Start X= %d, StartY= %d, dx= %d, dy= %d" % (startX, startY, dx,dy))
			
			startX=max(startX,0)
			startY=max(startY,0)			
			lenToExtractY = int( SCREENH / zoomValues[zoomIndex] )
			lenToExtractX = int( SCREENW / zoomValues[zoomIndex] )
			startY = min( int(startY / coeffSpeedMouse) , IMTOTH - lenToExtractY  ) *coeffSpeedMouse
			startX = min( int(startX / coeffSpeedMouse) , IMTOTW - lenToExtractX  ) *coeffSpeedMouse

			zoom = collage[int(startY / coeffSpeedMouse ) : int(startY / coeffSpeedMouse)+ lenToExtractY , int(startX /coeffSpeedMouse)   : int(startX /coeffSpeedMouse) + lenToExtractX  ] # line collumn => Y X
			height, width, channel = zoom.shape
			#print("Before Lanczos, Zoom : Height= %d, Width= %d " % ( height , width ) )
			
			zoom = cv2.resize(zoom, ( SCREENW, SCREENH), cv2.INTER_LANCZOS4)
			height, width, channel = zoom.shape
			#print("After Lanczos, Zoom :Height= %d, Width= %d " % ( height , width ) )
			

			img = pygame.image.frombuffer(zoom.tostring(), zoom.shape[1::-1],"RGB")
			windowSurface.blit(img, (0, 0))	
			pygame.display.flip()

			done = False
			reAcquire = False
			finished = False
			while not done and not reAcquire and not finished:
			
				if multilight == 0 :
					a=0
					reAcquire = True
					#print("test ")
					#done = True
				if askToToggleML == 1 :
					a=0
					reAcquire = True
					#print("test ")
					#done = True
				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						finished = True
						#sys.exit()
					elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == LEFTBUTTON or event.button == WHEELUP) :
						
						if zoomIndex < (len(zoomValues)-1):
							zoomIndex = zoomIndex+1						
							dy = ( SCREENH/2 * (1.0/zoomValues[zoomIndex] - 1.0/zoomValues[zoomIndex-1]) ) *coeffSpeedMouse
							dx = ( SCREENW/2 * (1.0/zoomValues[zoomIndex] - 1.0/zoomValues[zoomIndex-1]) ) *coeffSpeedMouse
							startX=startX-dx
							startY=startY-dy
						
						print ("zoom In to zoom index = %d" % zoomIndex)
						done = True
					elif event.type == pygame.MOUSEBUTTONDOWN and (event.button == RIGHTBUTTON or event.button == WHEELDOWN) :
						print ('zoom Out')
						if zoomIndex >0 :
							zoomIndex = zoomIndex-1						
							dy = ( SCREENH/2 * (1.0/zoomValues[zoomIndex] - 1.0/zoomValues[zoomIndex+1])) *coeffSpeedMouse
							dx = ( SCREENW/2 * (1.0/zoomValues[zoomIndex] - 1.0/zoomValues[zoomIndex+1]) ) *coeffSpeedMouse
							startX=startX-dx
							startY=startY-dy
						  
						print ("zoom Out to zoom index = %d" % zoomIndex)
						done = True


					elif event.type == pygame.KEYDOWN and event.key == K_SPACE: 
						print('space')
						reAcquire = True
					elif event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
						print('escape')
						finished = True
					elif event.type == pygame.KEYDOWN and event.key == K_PAGEUP:
						print('PAGEUP')
						coeffSpeedMouse=coeffSpeedMouse+1
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_l:   #L comme LED
						print('LED')
						GPIO.output(leftLedPin , GPIO.HIGH) 
						GPIO.output(centerLedPin , GPIO.HIGH)
						GPIO.output(rightLedPin , GPIO.HIGH)
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_m:   #m comme LED
						print('LED OFF')
						GPIO.output(leftLedPin , GPIO.LOW) 
						GPIO.output(centerLedPin , GPIO.LOW)
						GPIO.output(rightLedPin , GPIO.LOW)
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_s:   # s comme SingleLight
						print("SingleLight = On")
						GPIO.output(leftLedPin , GPIO.HIGH) 
						GPIO.output(centerLedPin , GPIO.HIGH)
						GPIO.output(rightLedPin , GPIO.HIGH)
						multilight=0
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_q:   # q comme quit SingleLight
						print("SignleLight = Off")
						GPIO.output(leftLedPin , GPIO.LOW) 
						GPIO.output(centerLedPin , GPIO.HIGH)
						GPIO.output(rightLedPin , GPIO.LOW)
						multilight=1
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_PAGEDOWN:
						print('PAGEDOWN')
						coeffSpeedMouse=max(coeffSpeedMouse-1,1)
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_UP:
						#print('key up')
						dx = 0
						dy = -100
						startX=startX+dx
						startY=startY+dy
						#pygame.mouse.set_pos([600,400])
						print("key UP:  dx=%d, dy=%d, StartX= %d, StartY= %d," % (dx,dy,startX,startY))
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_DOWN:
						#print('key down')
						dx = 0
						dy = 100
						startX=startX+dx
						startY=startY+dy
						#pygame.mouse.set_pos([600,400])
						print("key DOWN:  dx=%d, dy=%d, StartX= %d, StartY= %d," % (dx,dy,startX,startY))
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_LEFT:
						#print("key left")
						dx = -100
						dy = 0
						startX=startX+dx
						startY=startY+dy
						#pygame.mouse.set_pos([600,400])
						print("key LEFT:  dx=%d, dy=%d, StartX= %d, StartY= %d," % (dx,dy,startX,startY))
						done = True
					elif event.type == pygame.KEYDOWN and event.key == K_RIGHT:
						#print("key right")
						dx = 100
						dy = 0
						startX=startX+dx
						startY=startY+dy
						#pygame.mouse.set_pos([600,400])
						print("key RIGHT:  dx=%d, dy=%d, StartX= %d, StartY= %d," % (dx,dy,startX,startY))

						done = True

					elif event.type == pygame.MOUSEMOTION :
						(x,y) = event.pos
						dy =  SCREENH/2 - y  #SCREENW/2   J'y comprend rien aux axes ! 
						dx =  SCREENW/2 - x # - #SCREENH/2
						startX=startX-dx
						startY=startY-dy
						pygame.mouse.set_pos([SCREENW/2,SCREENH/2])
						print("event.pos x=%d, y=%d, dx=%d, dy=%d, StartX= %d, StartY= %d," % (x,y,dx,dy,startX,startY))
						
						done = True
				k = cv2.waitKey(25) & 0xFF



	print('exit')
	print("coeffSpeedMouse=%d" % coeffSpeedMouse )
	capture0.release()
	#capture1.release()
	cv2.destroyAllWindows()