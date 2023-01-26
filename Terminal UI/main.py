import os
import sys
import time
import pygame
from pygame.locals import *
import pygame.freetype

pygame.init()

termwidth = 120
termheight = 30

font = pygame.freetype.SysFont("Consolas", 16)
fontsize = (9, 16)
#font.size = fontsize

newline = chr(10)
blank = " "
fullblock = chr(9608)

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class ScreenArray:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.array = list()
		self.reset()

	def reset(self):
		self.array = [str(" " * self.width) for row in range(self.height)]
		
	def write_single(self, symbol, coords):
		x = round(coords[0])
		y = round(coords[1])
		symbol = str(symbol[0])
		if x >= self.width or y >= self.height:
			return
		self.array[y] = self.array[y][0:x] + symbol + self.array[y][x+1:self.width]
	
	def write_line(self, symbol, coords, length, vertical = False):
		x = round(coords[0])
		y = round(coords[1])
		symbol = str(symbol[0])
		if x >= self.width or y >= self.height:
			return
		if not vertical:
			if x + length >= self.width:
				length = self.width - x
			self.array[y] = self.array[y][0:x] + str(symbol * length) + self.array[y][x:x+length]
		elif vertical:
			if y + length >= self.height:
				length = self.height - y
			for row in range(length):
				self.array[y+row] = self.array[y+row][0:x] + symbol + self.array[y+row][x+1:self.width]
	
	def write_array(self, inputarray, coords):
		x = round(coords[0])
		y = round(coords[1])
		inputwidth = inputarray.width
		inputheight = inputarray.height
		if x >= self.width or y >= self.height:
			return
		if x + inputwidth >= self.width:
			inputwidth = self.width - x
		if y + inputheight >= self.height:
			inputheight = self.height - y
		for i in range(inputheight):
			self.array[y+i] = self.array[y+i][0:x] + inputarray.array[i][0:inputwidth] + self.array[y+i][x+inputwidth:self.width]
		

	def draw(self):
		drawstring = ""
		for row in self.array:
			drawstring += newline + row
		cls()
		sys.stdout.write(drawstring)
	
	def drawPygame(self,destinationSurface, position = (0, 0), fgcolor = (255, 255, 255), bgcolor = (0, 0, 0)):
		surface = pygame.Surface((self.width * fontsize[0], self.height * fontsize[1]))
		for i in range(len(self.array)):
			font.render_to(surface, (0, i * fontsize[1]), self.array[i], fgcolor=fgcolor, bgcolor=bgcolor)
		destinationSurface.blit(surface, position)

def main():
	pygameScreen = pygame.display.set_mode((termwidth * fontsize[0], termheight * fontsize[1]))

	mainscreen = ScreenArray(termwidth, termheight)
	subscreen = ScreenArray(40, 10)
	framenum = 0

	subscreen.write_line("X", (0, 0), 40)
	subscreen.write_line("X", (0, 10-1), 40)
	subscreen.write_line("X", (0, 0), 10, vertical=True)
	subscreen.write_line("X", (40-1, 0), 10, vertical=True)
	subscreenmessage = "Hello!"
	for i in range(len(subscreenmessage)):
		subscreen.write_single(subscreenmessage[i], (20 - int(len(subscreenmessage)/2) + i, 5))

	while True:
		for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit(0)
					elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
						sys.exit(0)

		mainscreen.reset()
		mainscreen.write_line(fullblock, (0, 0), termwidth)
		mainscreen.write_line(fullblock, (0, termheight-1), termwidth)
		mainscreen.write_line(fullblock, (0, 0), termheight, vertical=True)
		mainscreen.write_line(fullblock, (termwidth-1, 0), termheight, vertical=True)
		mainscreen.write_array(subscreen, (framenum*4,framenum))
		mainscreen.draw()

		pygameScreen.fill((0, 0, 0))
		mainscreen.drawPygame(pygameScreen, fgcolor = (100, 255, 100), bgcolor = (30, 80, 30))
		pygame.display.flip()

		time.sleep(.5)
		framenum += 1

if __name__ == '__main__':
	sys.exit(main())