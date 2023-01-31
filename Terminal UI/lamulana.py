import sys
import time
import pygame
from pygame.locals import *
import terminalUI

pygame.init()

termwidth = 64
termheight = 32
framerate = 60
fontsize = terminalUI.fontsize
screenwidth, screenheight = termwidth * fontsize[0], termheight * fontsize[1]

class protagonist:
	def __init__(self):
		self.position = [0,0]
		self.character = 'u'
		self.color = (0, 128, 0)

def main():
	pygameScreen = pygame.display.set_mode((screenwidth, screenheight))
	mainScreen = terminalUI.textSurface(termwidth, termheight)

	player = protagonist()

	while True:
		for event in pygame.event.get():
			if event.type == QUIT:
				sys.exit(0)
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					sys.exit(0)
				elif event.key in (K_LEFT, K_KP4):
					player.position[0] -= 1
				elif event.key in (K_RIGHT, K_KP6):
					player.position[0] += 1

		mainScreen.reset()
		pygameScreen.fill((0, 0, 0))
		mainScreen.write_single(player.character, player.position, player.color)
		mainScreen.drawPygame(pygameScreen)
		pygame.display.flip()
		time.sleep(1/framerate)

if __name__ == '__main__':
	sys.exit(main())
