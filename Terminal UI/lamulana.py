import sys
import time
import pygame
import terminalUI

pygame.init()

termwidth = 64
termheight = 32
framerate = 60
fontsize = terminalUI.fontsize
screenwidth, screenheight = termwidth * fontsize[0], termheight * fontsize[1]

def main():
	pygameScreen = pygame.display.set_mode((screenwidth, screenheight))
	mainScreen = terminalUI.textSurface(termwidth, termheight)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit(0)
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					sys.exit(0)

		mainScreen.reset()
		pygameScreen.fill((0, 0, 0))
		mainScreen.drawPygame(pygameScreen)
		pygame.display.flip()
		time.sleep(1/framerate)

if __name__ == '__main__':
	sys.exit(main())
