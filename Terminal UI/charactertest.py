import os
import sys
import time
import math
import pygame
from pygame.locals import *
import pygame.freetype
import terminalUI
import random

pygame.init()

termwidth = 150
termheight = 40

framerate = 60

# fontdir = "freefont-20120503"
# font = pygame.freetype.Font(os.path.join(fontdir, "FreeMono.otf"), 32) # https://www.fileformat.info/info/unicode/font/freemono/grid.htm <- Grid of supported characters
# font.strong = True
# fontsize = (20,32)

# fallbackfonts = list()
# fallbackfonts.append(pygame.freetype.Font(os.path.join(fontdir, "FreeSans.otf"), 32)) # https://www.fileformat.info/info/unicode/font/freeserif/grid.htm <- Grid of supported characters
# fallbackfonts.append(pygame.freetype.Font(os.path.join(fontdir, "FreeSerif.otf"), 32)) # https://www.fileformat.info/info/unicode/font/freeserif/grid.htm <- Grid of supported characters
# for fallbackfont in fallbackfonts:
# 	fallbackfont.strong = True

# terminalUI.setfont(font, fontsize)
# terminalUI.setfallbackfonts(fallbackfonts)

fontsize = terminalUI.fontsize

screenwidth, screenheight = termwidth * fontsize[0], termheight * fontsize [1]

def genstrings(screennum):
	strings = list()
	screenstart = screennum * termwidth * termheight
	for i in range(termheight):
		thisstring = ""
		rowstart = screenstart + (i * termwidth)
		for j in range(termwidth):
			if rowstart+j < 55296 or rowstart+j > 57343:
				thisstring += chr(rowstart+j)
			else:
				thisstring += " "
		strings.append(thisstring)
	print(f"Screen {screennum}: {screennum*termwidth*termheight} - {(screennum+1)*termwidth*termheight}")
	return strings


def main():
	pygameScreen = pygame.display.set_mode((termwidth * fontsize[0], termheight * fontsize[1]))
	mainscreen = terminalUI.textSurface(termwidth, termheight)

	framenum = 0
	screennum = 0
	strings = genstrings(screennum)
	screenchanged = True

	while True:
		for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit(0)
					elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
						sys.exit(0)
		
		keyspressed = pygame.key.get_pressed()
		if keyspressed[K_LEFT] or keyspressed[K_KP4]:
			if screennum > 0:
				screennum -= 1
				strings = genstrings(screennum)
				screenchanged = True
			

		if keyspressed[K_RIGHT] or keyspressed[K_KP6]:
			screennum += 1
			strings = genstrings(screennum)
			screenchanged = True

		if screenchanged:
			mainscreen.reset()
			for i in range(termheight):
				mainscreen.write_string(strings[i], (0,i))

			pygameScreen.fill((0, 0, 0))
			mainscreen.drawPygame(pygameScreen)
			pygame.display.flip()
			screenchanged = False
		

		time.sleep(1/framerate)
		framenum += 1

if __name__ == '__main__':
	sys.exit(main())
