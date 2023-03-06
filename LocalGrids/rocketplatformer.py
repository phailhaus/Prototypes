import sys
import math
import pygame
import pygame.gfxdraw
from pygame.locals import *
import pymunk
import pymunk.pygame_util

from localgrids import Localgrid
from cameraTransform import cameraTransform

pygame.init()

clock = pygame.time.Clock()

screenwidth = 800
screenheight = 600
screensize = (screenwidth, screenheight)

framerate = 60

def main():
	screen = pygame.display.set_mode(screensize)

	cameraposition = pygame.Vector2(0, 0)
	camerarotation = 0
	camerascale = 1

	while True:
		for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit(0)
					elif event.type == KEYDOWN:
						if event.key == K_ESCAPE:
							sys.exit(0)

		keyspressed = pygame.key.get_pressed()
		if keyspressed[K_UP] or keyspressed[K_KP8]: cameraposition -= pygame.Vector2(0, 1).rotate(-camerarotation * 360) # Up
		if keyspressed[K_DOWN] or keyspressed[K_KP5]: cameraposition += pygame.Vector2(0, 1).rotate(-camerarotation * 360) # Down
		if keyspressed[K_LEFT] or keyspressed[K_KP4]: cameraposition -= pygame.Vector2(1, 0).rotate(-camerarotation * 360) # Left
		if keyspressed[K_RIGHT] or keyspressed[K_KP6]: cameraposition += pygame.Vector2(1, 0).rotate(-camerarotation * 360) # Right
		if keyspressed[K_KP7]: camerarotation -= .1/framerate # Rotate counter-clockwise
		if keyspressed[K_KP9]: camerarotation += .1/framerate # Rotate clockwise
		if keyspressed[K_KP_PLUS]: camerascale += .1/framerate # Zoom in
		if keyspressed[K_KP_MINUS]: camerascale -= .1/framerate # Zoom out

		screen.fill((0, 0, 0))

		pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(100, 100, screenwidth - 200, screenheight - 200), 2)
		
		squigglepoints = list()
		for i in range(6):
			y = (i * 50) + 50
			for x in (50, 200):
				squigglepoints.append(cameraTransform(screen, (x, y), cameraposition, camerarotation, camerascale))
			
		pygame.draw.aalines(screen, (255,255,255), False, squigglepoints)

		pygame.display.flip()

		clock.tick(framerate)
		#print(clock.get_fps())

if __name__ == '__main__':
	sys.exit(main())

