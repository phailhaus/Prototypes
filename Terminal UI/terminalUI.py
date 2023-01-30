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

class textSurface: # Similar in concept to a Pygame surface but with text instead of pixels
	def __init__(self, width, height, defaultfgcolor = (255, 255, 255), defaultbgcolor = (0, 0, 0)):
		self.width = width
		self.height = height
		self.defaultfgcolor = defaultfgcolor
		self.defaultbgcolor = defaultbgcolor
		self.array = list()
		self.colorarray = list()
		self.reset()

	def reset(self): # Blank the surface
		self.array = [str(" " * self.width) for i in range(self.height)]
		self.colorarray = [[(self.defaultfgcolor, self.defaultbgcolor) for j in range(self.width)] for i in range(self.height)]

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
		
	def write_single(self, symbol, coords, fgcolor=None, bgcolor=None): # Write a single character to a specified position
		x = math.floor(coords[0])
		y = math.floor(coords[1])
		symbol = str(str(symbol)[0])
		if x >= self.width or x < 0 or y >= self.height or y < 0:
			return
		self.array[y] = self.array[y][0:x] + symbol + self.array[y][x+1:self.width]
		if fgcolor != None:
			self.colorarray[y][x] = (fgcolor, self.colorarray[y][x][1])
		if bgcolor != None:
			self.colorarray[y][x] = (self.colorarray[y][x][0], bgcolor)
	
	def write_string(self, string, coords, angle=0, fgcolor=None, bgcolor=None): # Write a string to the surface. Defaults to right, rotates clockwise
		x = coords[0]
		y = coords[1]
		string = str(string)
		offsetlist = self.calc_slope(len(string), angle)
		for i in range(len(string)):
			xoff = offsetlist[i][0]
			yoff = offsetlist[i][1]
			self.write_single(string[i], (x+xoff, y+yoff), fgcolor, bgcolor)

	def write_line(self, symbol, length, coords, angle=0, variablelength = False, fgcolor=None, bgcolor=None): # Write a line of the same character. If variablelength is off, writes length characters, like writestring. If variablelength is on, reduces number of characters at angles to give similar length to a cardinal line
		symbol = str(str(symbol)[0])
		if variablelength:
			length = round(length * math.cos(math.radians(((angle + 45) % 90)-45)))
		self.write_string(symbol * length, coords, angle, fgcolor, bgcolor)
	
	def write_rectangle(self, symbol, coords, width, height, angle=0, fromcenter=False, filled=False, filledsymbol=" ", fgcolor=None, bgcolor=None): # Write a line of the same character. If variablelength is off, writes length characters, like writestring. If variablelength is on, reduces number of characters at angles to give similar length to a cardinal line
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
				self.write_line(filledsymbol, width, (coords[0] + leftedgeoffsets[i][0], coords[1] + leftedgeoffsets[i][1]), angle, fgcolor = fgcolor, bgcolor = bgcolor) # Draw a line parallel to the top edge from each point on the left edge 
				a = leftedgeoffsets[0][0]
				b = leftedgeoffsets[i][0] + math.copysign(1, topedgeoffsets[-1][0])
				c = leftedgeoffsets[-1][0]
				if (a <= b <= c) or (c <= b <= a):
					self.write_line(filledsymbol, width-1, (coords[0] + b, coords[1] + leftedgeoffsets[i][1]), angle, fgcolor = fgcolor, bgcolor = bgcolor) # Draw extra lines offset by one X in the direction the top edge is going to fill gaps at angles
		
		self.write_line(symbol, width, coords, angle, fgcolor = fgcolor, bgcolor = bgcolor) # Top
		self.write_line(symbol, height, coords, angle+90, fgcolor = fgcolor, bgcolor = bgcolor) # Left
		self.write_line(symbol, width, bottomleftcorner, angle, fgcolor = fgcolor, bgcolor = bgcolor) # Bottom
		self.write_line(symbol, height, toprightcorner, angle+90, fgcolor = fgcolor, bgcolor = bgcolor) # Right
	
	def write_surface(self, inputarray, coords, angle=0, fromcenter=False): # Write a different surface onto this one
		inputwidth = inputarray.width
		inputheight = inputarray.height
		if fromcenter:
			fromcenteroffsetleft = self.calc_slope(inputwidth/2, angle+180)[-1]
			fromcenteroffsetup = self.calc_slope(inputheight/2, angle+270)[-1]
			fromcenteroffset = (fromcenteroffsetleft[0] + fromcenteroffsetup[0], fromcenteroffsetleft[1] + fromcenteroffsetup[1])
			coords = (coords[0] + fromcenteroffset[0], coords[1] + fromcenteroffset[1])
		self.write_rectangle(" ", coords, inputwidth, inputheight, angle, filled=True, fgcolor=inputarray.defaultfgcolor, bgcolor=inputarray.defaultbgcolor)
		topedgeoffsets = self.calc_slope(inputwidth, angle)
		leftedgeoffsets = self.calc_slope(inputheight, angle+90)
		for i in range(inputheight):
			for j in range(inputwidth):
				self.write_single(inputarray.array[i][j], (coords[0] + topedgeoffsets[j][0] + leftedgeoffsets[i][0], coords[1] + topedgeoffsets[j][1] + leftedgeoffsets[i][1]), inputarray.colorarray[i][j][0], inputarray.colorarray[i][j][1])
		

	def draw(self): # Draw the surface to the terminal
		drawstring = ""
		for row in self.array:
			drawstring += newline + row
		os.system('cls' if os.name=='nt' else 'clear')
		sys.stdout.write(drawstring)
	
	def drawPygame(self,destinationSurface, position = (0, 0)): # Draw the surface to a given Pygame surface
		surface = pygame.Surface((self.width * fontsize[0], self.height * fontsize[1]))
		for i in reversed(range(self.height)):
			for j in range(self.width):
				if self.array[i][j] != " ":
					charmetrics = font.get_metrics(self.array[i][j])[0]
					charactersurface = pygame.Surface((fontsize[0], fontsize[1] - min(charmetrics[2], 0)), SRCALPHA) # Generate surface the size of a character
				else:
					charactersurface = pygame.Surface((fontsize[0], fontsize[1]), SRCALPHA) # Generate surface the size of a character
				charactersurface.fill(self.colorarray[i][j][1], pygame.Rect(0, 0, fontsize[0], fontsize[1])) # Fill surface with character BG color, but only the normal bounds. Leave descender area transparent
				if self.array[i][j] != " ":
					characterrect = font.get_rect(self.array[i][j])
					characterrect.midbottom = (fontsize[0]/2, fontsize[1]-charmetrics[2]-1) # Center horizontally and use metrics to place vertically
					font.render_to(charactersurface, characterrect, text=None, fgcolor=self.colorarray[i][j][0])
				surface.blit(charactersurface, (j * fontsize[0], i * fontsize[1]))
		destinationSurface.blit(surface, position)

def main():
	pygameScreen = pygame.display.set_mode((termwidth * fontsize[0], termheight * fontsize[1]))

	mainscreen = textSurface(termwidth, termheight, defaultfgcolor = (100, 255, 100), defaultbgcolor = (30, 80, 30))
	subscreen = textSurface(20, 10)
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