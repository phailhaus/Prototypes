import sys
import math
import pygame
import pygame.gfxdraw
from pygame.locals import *
import pymunk
import pymunk.pygame_util

from localgrids import Localgrid
import cameraTransform

pygame.init()

clock = pygame.time.Clock()

screenwidth = 800
screenheight = 600
screensize = (screenwidth, screenheight)

framerate = 60

def main():
	screen = pygame.display.set_mode(screensize)
	camera = cameraTransform.Camera()

	while True:
		for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit(0)
					elif event.type == KEYDOWN:
						if event.key == K_ESCAPE:
							sys.exit(0)

		keyspressed = pygame.key.get_pressed()
		if keyspressed[K_UP] or keyspressed[K_KP8]: camera.move(y = -1) # Up
		if keyspressed[K_DOWN] or keyspressed[K_KP5]: camera.move(y = 1) # Down
		if keyspressed[K_LEFT] or keyspressed[K_KP4]: camera.move(x = -1) # Left
		if keyspressed[K_RIGHT] or keyspressed[K_KP6]: camera.move(x = 1) # Right
		if keyspressed[K_KP7]: camera.rotate(-30/framerate) # Rotate counter-clockwise
		if keyspressed[K_KP9]: camera.rotate(30/framerate) # Rotate clockwise
		if keyspressed[K_KP_PLUS]: camera.zoom(.1/framerate) # Zoom in
		if keyspressed[K_KP_MINUS]: camera.zoom(-.1/framerate) # Zoom out

		screen.fill((0, 0, 0))

		pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(100, 100, screenwidth - 200, screenheight - 200), 2)
		
		squigglepoints = list()
		for i in range(6):
			y = (i * 50) + 50
			for x in (50, 200):
				squigglepoints.append(camera.transformCoord(screen, (x, y)))
			
		pygame.draw.aalines(screen, (255,255,255), False, squigglepoints)

		pygame.display.flip()

		clock.tick(framerate)
		#print(clock.get_fps())

if __name__ == '__main__':
	sys.exit(main())

