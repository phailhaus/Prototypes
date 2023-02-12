import os
import sys
import math
import pygame
from pygame.locals import *
import pygame.freetype

pygame.init()
fontdir = "freefont-20120503"
font = pygame.freetype.Font(os.path.join(fontdir, "FreeMono.otf"), 16) # https://www.fileformat.info/info/unicode/font/freemono/grid.htm <- Grid of supported characters
font.strong = True
font.ucs4 = True
fontsize = (10,16)

glyphcache = dict()

fallbackfonts = list()
fallbackfonts.append(pygame.freetype.Font(os.path.join(fontdir, "FreeSans.otf"), 16)) # https://www.fileformat.info/info/unicode/font/freeserif/grid.htm <- Grid of supported characters
fallbackfonts.append(pygame.freetype.Font(os.path.join(fontdir, "FreeSerif.otf"), 16)) # https://www.fileformat.info/info/unicode/font/freeserif/grid.htm <- Grid of supported characters
for fallbackfont in fallbackfonts:
	fallbackfont.strong = True
	fallbackfont.ucs4 = True

def setfont(newfont, newsize): # Function to override default font with a new one
	global font
	global fontsize
	font = newfont
	fontsize = newsize

def setfallbackfonts(newfonts): # Function to override default fallback font list with a new one. Must be a list.
	global fallbackfonts
	fallbackfonts = newfonts

newline = chr(10)

class textSurface: # Similar in concept to a Pygame surface but with text instead of pixels
	def __init__(self, width, height, defaultfgcolor = (255, 255, 255), defaultbgcolor = (0, 0, 0)):
		self.width = width
		self.height = height
		self.defaultfgcolor = defaultfgcolor
		self.defaultbgcolor = defaultbgcolor
		self.array = list()
		self.colorarray = list()
		self.modifierarray = list() # "mirror_horizontal" or "mh" to flip the character horizontally. "mirror_vertical" or "mv" to flip it vertically, which doesn't handle descenders well
		global glyphcache
		self.reset()

	def reset(self): # Blank the surface
		self.array = [[" " for j in range(self.width)] for i in range(self.height)]
		self.colorarray = [[(self.defaultfgcolor, self.defaultbgcolor) for j in range(self.width)] for i in range(self.height)]
		self.modifierarray = [[None for j in range(self.width)] for i in range(self.height)]

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
		if angle == -45:
			slope = -1
		else:
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
	
	def calc_slope_destination(self, source=(0,0), destination=(0,0), length=1): # Feeds calc_slope with angle and length based on source and destination coords
		if source != destination:
			dx = destination[0] - source[0]
			dy = destination[1] - source[1]
			deg0 = pygame.math.Vector2(1, 0)
			targetvec = pygame.math.Vector2(dx, dy)
			angle = deg0.angle_to(targetvec)
			length = max(max(abs(dx), abs(dy)) + 1, length)
			offsetlist = self.calc_slope(length, angle)
		else:
			offsetlist = list()
			offsetlist.append((0,0))
		return offsetlist
		
	def write_single(self, symbol, coords, fgcolor=None, bgcolor=None, modifiers=None): # Write a single character to a specified position
		x = math.floor(coords[0])
		y = math.floor(coords[1])
		symbol = str(str(symbol)[0])
		if x >= self.width or x < 0 or y >= self.height or y < 0:
			return
		self.array[y][x] = symbol
		if fgcolor != None:
			self.colorarray[y][x] = (fgcolor, self.colorarray[y][x][1])
		if bgcolor != None:
			self.colorarray[y][x] = (self.colorarray[y][x][0], bgcolor)
		if type(modifiers) == str:
			modifiers = (modifiers,)
		if type(modifiers) == tuple:
			self.modifierarray[y][x] = modifiers
	
	def write_string(self, string, coords, angle=0, destcoords = None, fgcolor=None, bgcolor=None, modifiers=None): # Write a string to the surface. Defaults to right, rotates clockwise. If destcoords is set, overrides angle with the direction of destcoords from coords
		x = coords[0]
		y = coords[1]
		string = str(string)
		if destcoords == None:
			offsetlist = self.calc_slope(len(string), angle)
		else:
			offsetlist = self.calc_slope_destination(coords, destcoords, len(string))
		thismod = modifiers
		for i in range(len(string)):
			xoff = offsetlist[i][0]
			yoff = offsetlist[i][1]
			if type(modifiers) == list and len(modifiers) == len(string):
				thismod = modifiers[i]
			self.write_single(string[i], (x+xoff, y+yoff), fgcolor, bgcolor, modifiers=thismod)

	def write_line(self, symbol, length = None, coords = (0,0), angle=0, destcoords = None, variablelength = False, fgcolor=None, bgcolor=None, modifiers=None): # Write a line of the same character. If variablelength is off, writes length characters, like writestring. If variablelength is on, reduces number of characters at angles to give similar length to a cardinal line. If destcoords is set, overrides angle with the direction of destcoords from coords. Can calculate length to destination, but takes length if given
		symbol = str(str(symbol)[0])
		if length != None:
			if variablelength:
				length = round(length * math.cos(math.radians(((angle + 45) % 90)-45)))
			else:
				length = round(length)
		elif length == None and destcoords != None:
			dx = destcoords[0] - coords[0]
			dy = destcoords[1] - coords[1]
			length = math.floor(max(abs(dx), abs(dy)) + 1)
		else:
			length = 1

		self.write_string(symbol * length, coords, angle, destcoords, fgcolor, bgcolor, modifiers=modifiers)

	
	def write_rectangle(self, symbol, coords, width, height, angle=0, fromcenter=False, filled=False, filledsymbol=" ", fgcolor=None, bgcolor=None, modifiers=None, fillmodifiers=None): # Write a line of the same character. If variablelength is off, writes length characters, like writestring. If variablelength is on, reduces number of characters at angles to give similar length to a cardinal line
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
				self.write_line(filledsymbol, width, (coords[0] + leftedgeoffsets[i][0], coords[1] + leftedgeoffsets[i][1]), angle, fgcolor = fgcolor, bgcolor = bgcolor, modifiers=fillmodifiers) # Draw a line parallel to the top edge from each point on the left edge 
				a = leftedgeoffsets[0][0]
				b = leftedgeoffsets[i][0] + math.copysign(1, topedgeoffsets[-1][0])
				c = leftedgeoffsets[-1][0]
				if angle % 90 != 0 and ((a <= b <= c) or (c <= b <= a)):
					self.write_line(filledsymbol, width-1, (coords[0] + b, coords[1] + leftedgeoffsets[i][1]), angle, fgcolor = fgcolor, bgcolor = bgcolor, modifiers=fillmodifiers) # Draw extra lines offset by one X in the direction the top edge is going to fill gaps at angles
		
		self.write_line(symbol, width, coords, angle, fgcolor = fgcolor, bgcolor = bgcolor, modifiers=modifiers) # Top
		self.write_line(symbol, height, coords, angle+90, fgcolor = fgcolor, bgcolor = bgcolor, modifiers=modifiers) # Left
		self.write_line(symbol, width, bottomleftcorner, angle, fgcolor = fgcolor, bgcolor = bgcolor, modifiers=modifiers) # Bottom
		self.write_line(symbol, height, toprightcorner, angle+90, fgcolor = fgcolor, bgcolor = bgcolor, modifiers=modifiers) # Right
	
	def write_surface(self, inputarray, coords, angle=0, fromcenter=False): # Write a different surface onto this one
		inputwidth = inputarray.width
		inputheight = inputarray.height
		if fromcenter:
			fromcenteroffsetleft = self.calc_slope(inputwidth/2, angle+180)[-1]
			fromcenteroffsetup = self.calc_slope(inputheight/2, angle+270)[-1]
			fromcenteroffset = (fromcenteroffsetleft[0] + fromcenteroffsetup[0], fromcenteroffsetleft[1] + fromcenteroffsetup[1])
			coords = (coords[0] + fromcenteroffset[0], coords[1] + fromcenteroffset[1])
		if angle % 90 != 0:
			self.write_rectangle(" ", coords, inputwidth, inputheight, angle, filled=True, fgcolor=inputarray.defaultfgcolor, bgcolor=inputarray.defaultbgcolor)
		topedgeoffsets = self.calc_slope(inputwidth, angle)
		leftedgeoffsets = self.calc_slope(inputheight, angle+90)
		for i in range(inputheight):
			for j in range(inputwidth):
				self.write_single(inputarray.array[i][j], (coords[0] + topedgeoffsets[j][0] + leftedgeoffsets[i][0], coords[1] + topedgeoffsets[j][1] + leftedgeoffsets[i][1]), inputarray.colorarray[i][j][0], inputarray.colorarray[i][j][1], inputarray.modifierarray[i][j])
		

	def draw(self): # Draw the surface to the terminal
		drawstring = ""
		for row in self.array:
			drawstring += newline
			for symbol in row:
				drawstring += symbol
		os.system('cls' if os.name=='nt' else 'clear')
		sys.stdout.write(drawstring)
	
	def drawPygame(self,destinationSurface, position = (0, 0)): # Draw the surface to a given Pygame surface
		surface = pygame.Surface((self.width * fontsize[0], self.height * fontsize[1]), SRCALPHA)
		surface.fill(color=self.defaultbgcolor)
		batchwidth = 0
		batchcolor = None
		for i in range(self.height): # Draw background
			batchwidth = 0
			batchcolor = None
			for j in range(self.width):
				thiscolor = self.colorarray[i][j][1]
				if batchwidth == 0 or batchcolor == thiscolor: # Start or extend batch if it matches
					batchwidth += 1
					batchcolor = thiscolor
				else: # If it doesn't match, write the previous batch and start a new one
					if batchcolor != self.defaultbgcolor: 
						backgroundrect = pygame.Rect(((j-batchwidth) * fontsize[0], (i * fontsize[1])), (fontsize[0]*batchwidth, fontsize[1]))
						surface.fill(color=batchcolor, rect=backgroundrect)
					batchwidth = 1
					batchcolor = thiscolor
			if batchcolor != self.defaultbgcolor:# End of line, write lingering batch
				backgroundrect = pygame.Rect(((self.width-batchwidth) * fontsize[0], (i * fontsize[1])), (fontsize[0]*batchwidth, fontsize[1]))
				surface.fill(color=batchcolor, rect=backgroundrect)
		charactertodraw = None
		characterfgcolor = None
		charactermodifiers = None
		for i in range(self.height):
			for j in range(self.width):
				if self.array[i][j] != " ": # Draw nothing if character is space, otherwise draw
					if self.array[i][j] == charactertodraw and self.colorarray[i][j][0] == characterfgcolor and self.modifierarray[i][j] == charactermodifiers: # If it is exactly the same as the last character drawn, just use the last charactersurface again
						surface.blit(charactersurface, ((j - .5) * fontsize[0], (i - .5) * fontsize[1])) # Draw to working surface
					else:
						charactertodraw = self.array[i][j]
						characterfgcolor = self.colorarray[i][j][0]
						charactermodifiers = self.modifierarray[i][j]
						if (charactertodraw, characterfgcolor, charactermodifiers) in glyphcache:
							charactersurface = glyphcache[(charactertodraw, characterfgcolor, charactermodifiers)]
							surface.blit(charactersurface, ((j - .5) * fontsize[0], (i - .5) * fontsize[1])) # Draw to working surface
						else:
							currentfont = None
							if font.get_metrics(charactertodraw)[0] != None: # Set font to default if drawing space or if default has character
								currentfont = font
							else:
								for fallbackfont in fallbackfonts: # Cycle through fallbacks to find character
									if fallbackfont.get_metrics(charactertodraw)[0] != None:
										currentfont = fallbackfont
										break
							if currentfont == None: # Give up, replace character with space
								charactertodraw = " "
								currentfont = font
							if charactertodraw != " ": # Draw nothing if character is space, otherwise draw
								charmetric = currentfont.get_metrics(charactertodraw)[0][2]
								if charmetric > 2 ** 31: # Check for unsigned int with rollover
									charmetric -= 2 ** 32 # Convert to signed int
								charactersurface = pygame.Surface((fontsize[0] * 2, fontsize[1] * 2), SRCALPHA) # Generate surface the size of a character * 2 in each direction
								characterrect = currentfont.get_rect(charactertodraw)
								characterrect.midbottom = (fontsize[0], (fontsize[1] * 1.5) - charmetric) # Center horizontally and use metrics to place vertically
								currentfont.render_to(charactersurface, characterrect, text=None, fgcolor=characterfgcolor) # Draw character to intermediate surface
								flip_x, flip_y = False, False
								if charactermodifiers != None:
									if "mirror_horizontal" in charactermodifiers or "mh" in charactermodifiers:
										flip_x = True
									if "mirror_vertical" in charactermodifiers or "mv" in charactermodifiers:
										flip_y = True
									if flip_x == True or flip_y == True:
										charactersurface = pygame.transform.flip(charactersurface, flip_x, flip_y) # Mirror the character if needed
								glyphcache[(charactertodraw, characterfgcolor, charactermodifiers)] = charactersurface
								surface.blit(charactersurface, ((j - .5) * fontsize[0], (i - .5) * fontsize[1])) # Draw to working surface
		destinationSurface.blit(surface, position) # Draw to output surface
