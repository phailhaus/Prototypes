import sys
import time
import pygame
from pygame.locals import *
import pygame.freetype
import terminalUI

pygame.init()

termwidth = 120
termheight = 30

#font = pygame.freetype.SysFont("Consolas", 16)
font = pygame.freetype.Font("freefont-20120503\FreeMonoBold.otf", 16)
fontsize = (9, 16) # Pygame window is (termwidth * fontsize[0], termheight * fontsize[1]). With antiailiased Consolas at 16, this should be (9, 16) 

terminalUI.setfont(font, fontsize)

fullblock = chr(9608)

def main():
	pygameScreen = pygame.display.set_mode((termwidth * fontsize[0], termheight * fontsize[1]))

	mainscreen = terminalUI.textSurface(termwidth, termheight, defaultfgcolor = (100, 255, 100), defaultbgcolor = (30, 80, 30))
	subscreen = terminalUI.textSurface(20, 10)
	framenum = 0

	subscreen.write_rectangle("X", (0,0), subscreen.width, subscreen.height)
	subscreen.write_string("Periods are gaps!", (10 - int(len("Periods are gaps!")/2), 5))

	testangle = 45

	while True:
		for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit(0)
					elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
						sys.exit(0)

		mainscreen.reset()
		mainscreen.write_rectangle(fullblock, (0, 0), termwidth, termheight)


		mainscreen.write_rectangle("A", (20, 15), 7, 5, testangle, fromcenter=True)
		mainscreen.write_rectangle("F", (35, 15), 9, 7, testangle, fromcenter=True, filled=True, filledsymbol=".", fgcolor=(100, 100, 255), bgcolor=(50, 50, 120))
		mainscreen.write_line("B", 14, (termwidth-20, 15), testangle, variablelength=True)
		#mainscreen.write_string("ANGLES!", (60, 15), testangle)
		mainscreen.write_rectangle("F", (60, 15), 20, 10, testangle, fromcenter=True, filled=True, filledsymbol=".")
		mainscreen.write_surface(subscreen, (60,15), testangle, fromcenter=True)
		mainscreen.write_string("-_-_-", (10, 5), fgcolor=(255, 100, 100), bgcolor=(120, 50, 50))
		

		#mainscreen.draw()

		pygameScreen.fill((0, 0, 0))
		mainscreen.drawPygame(pygameScreen)
		pygame.display.flip()

		time.sleep(.1)
		#testangle += 5
		framenum += 1

if __name__ == '__main__':
	sys.exit(main())