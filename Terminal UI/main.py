import os
import sys
import time
import math
import pygame
from pygame.locals import *
import pygame.freetype

pygame.init()

termwidth = 120
termheight = 30

font = pygame.freetype.SysFont("Consolas", 16)
fontsize = (9, 16) # Pygame window is (termwidth * fontsize[0], termheight * fontsize[1]). With antiailiased Consolas at 16, this should be (9, 16) 
#font.size = (16,16)

newline = chr(10)
blank = " "
fullblock = chr(9608)

def cls(): # Clears terminals
    os.system('cls' if os.name=='nt' else 'clear')

class textSurface: # Similar in concept to a Pygame surface but with text instead of pixels
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.array = list()
		self.reset()

	def reset(self): # Blank the surface
		self.array = [str(" " * self.width) for i in range(self.height)]

	def calc_slope(self, length, angle): # Calculates how each successive character should be offset from the starting coords
		offsetlist = list()
		length = math.ceil(length)
		angle = angle % 360
		x = 0
		y = 0

		direction = "R"
		if 45 <= angle < 135:
			direction = "D"
		elif 135 <= angle < 225:
			direction = "L"
		elif 225 <= angle < 315:
			direction = "U"
		
		angle = ((angle + 45) % 90) - 45
		
		slope = math.tan(math.radians(angle))
		slope = min(slope, 1)
		slope = max(slope, -1)
		for i in range(length):
			if direction == "R":
				offsetlist.append((math.floor(x), math.floor(y)))
				x += 1
				y += slope
			elif direction == "D":
				offsetlist.append((math.floor(x), math.floor(y)))
				x -= slope
				y += 1
			elif direction == "L":
				offsetlist.append((math.floor(x), math.floor(y)))
				x -= 1
				y -= slope
			elif direction == "U":
				offsetlist.append((math.floor(x), math.floor(y)))
				x += slope
				y -= 1
		return offsetlist
		
	def write_single(self, symbol, coords): # Write a single character to a specified position
		x = math.floor(coords[0])
		y = math.floor(coords[1])
		symbol = str(str(symbol)[0])
		if x >= self.width or x < 0 or y >= self.height or y < 0:
			return
		self.array[y] = self.array[y][0:x] + symbol + self.array[y][x+1:self.width]
	
	def write_string(self, string, coords, angle=0): # Write a string to the surface. Defaults to right, rotates clockwise
		x = coords[0]
		y = coords[1]
		string = str(string)
		offsetlist = self.calc_slope(len(string), angle)
		for i in range(len(string)):
			xoff = offsetlist[i][0]
			yoff = offsetlist[i][1]
			self.write_single(string[i], (x+xoff, y+yoff))

	def write_line(self, symbol, length, coords, angle=0, variablelength = False): # Write a line of the same character. If variablelength is off, writes length characters, like writestring. If variablelength is on, reduces number of characters at angles to give similar length to a cardinal line
		symbol = str(str(symbol)[0])
		if variablelength:
			length = round(length * math.cos(math.radians(((angle + 45) % 90)-45)))
		self.write_string(symbol * length, coords, angle)
	
	def write_rectangle(self, symbol, coords, width, height, angle=0, fromcenter=False, filled=False, filledsymbol=" "): # Write a line of the same character. If variablelength is off, writes length characters, like writestring. If variablelength is on, reduces number of characters at angles to give similar length to a cardinal line
		symbol = str(str(symbol)[0])
		filledsymbol = str(str(filledsymbol)[0])
		if fromcenter:
			fromcenteroffsetleft = self.calc_slope(width/2, angle+180)[-1]
			fromcenteroffsetup = self.calc_slope(height/2, angle+270)[-1]
			fromcenteroffset = (fromcenteroffsetleft[0] + fromcenteroffsetup[0], fromcenteroffsetleft[1] + fromcenteroffsetup[1])
			coords = (coords[0] + fromcenteroffset[0], coords[1] + fromcenteroffset[1])
		
		topedgeoffsets = self.calc_slope(width, angle)
		leftedgeoffsets = self.calc_slope(height, angle+90)
		toprightcorner = (coords[0] + topedgeoffsets[-1][0], coords[1] + topedgeoffsets[-1][1])
		bottomleftcorner = (coords[0] + leftedgeoffsets[-1][0], coords[1] + leftedgeoffsets[-1][1])
		
		if filled:
			for i in range(height):
				self.write_line(filledsymbol, width, (coords[0] + leftedgeoffsets[i][0], coords[1] + leftedgeoffsets[i][1]), angle)
		
		self.write_line(symbol, width, coords, angle) # Top
		self.write_line(symbol, height, coords, angle+90) # Left
		self.write_line(symbol, width, bottomleftcorner, angle) # Bottom
		self.write_line(symbol, height, toprightcorner, angle+90) # Right
	
	def write_surface(self, inputarray, coords, angle=0, fromcenter=False): # Write a different surface onto this one
		inputwidth = inputarray.width
		inputheight = inputarray.height
		if fromcenter:
			fromcenteroffsetleft = self.calc_slope(inputwidth/2, angle+180)[-1]
			fromcenteroffsetup = self.calc_slope(inputheight/2, angle+270)[-1]
			fromcenteroffset = (fromcenteroffsetleft[0] + fromcenteroffsetup[0], fromcenteroffsetleft[1] + fromcenteroffsetup[1])
			coords = (coords[0] + fromcenteroffset[0], coords[1] + fromcenteroffset[1])
		leftedgeoffsets = self.calc_slope(inputheight, angle+90)
		for i in range(inputheight):
			self.write_string(inputarray.array[i], (coords[0] + leftedgeoffsets[i][0], coords[1] + leftedgeoffsets[i][1]), angle)
		

	def draw(self): # Draw the surface to the terminal
		drawstring = ""
		for row in self.array:
			drawstring += newline + row
		cls()
		sys.stdout.write(drawstring)
	
	def drawPygame(self,destinationSurface, position = (0, 0), fgcolor = (255, 255, 255), bgcolor = (0, 0, 0)): # Draw the surface to a given Pygame surface
		surface = pygame.Surface((self.width * fontsize[0], self.height * fontsize[1]))
		for i in range(len(self.array)):
			font.render_to(surface, (0, i * fontsize[1]), self.array[i], fgcolor=fgcolor, bgcolor=bgcolor)
		destinationSurface.blit(surface, position)

def main():
	pygameScreen = pygame.display.set_mode((termwidth * fontsize[0], termheight * fontsize[1]))

	mainscreen = textSurface(termwidth, termheight)
	subscreen = textSurface(20, 10)
	framenum = 0

	subscreen.write_rectangle("X", (0,0), subscreen.width, subscreen.height)
	subscreen.write_string("Hello!", (10 - int(len("Hello!")/2), 5))

	testangle = 0

	while True:
		for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit(0)
					elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
						sys.exit(0)

		mainscreen.reset()
		mainscreen.write_line(fullblock, termwidth, (0, 0))
		mainscreen.write_line(fullblock, termwidth, (0, termheight-1))
		mainscreen.write_line(fullblock, termheight, (0, 0), angle=90)
		mainscreen.write_line(fullblock, termheight, (termwidth-1, 0), angle=90)

		mainscreen.write_rectangle("A", (20, 15), 7, 5, testangle, fromcenter=True)
		mainscreen.write_rectangle("F", (35, 15), 9, 7, testangle, fromcenter=True, filled=True, filledsymbol=".")
		mainscreen.write_line("B", 14, (termwidth-20, 15), testangle, variablelength=True)
		mainscreen.write_string("ANGLES!", (60, 15), testangle)
		mainscreen.write_surface(subscreen, (60,15), testangle, fromcenter=True)
		

		mainscreen.draw()

		pygameScreen.fill((0, 0, 0))
		mainscreen.drawPygame(pygameScreen, fgcolor = (100, 255, 100), bgcolor = (30, 80, 30))
		pygame.display.flip()

		time.sleep(.1)
		testangle += 5
		framenum += 1

if __name__ == '__main__':
	sys.exit(main())