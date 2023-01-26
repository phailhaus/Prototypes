import os
import sys
from sys import stdout
import time
import numpy as np

termwidth = 120
termheight = 30

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
		stdout.write(drawstring)
    
mainscreen = ScreenArray(termwidth, termheight)
subscreen = ScreenArray(40, 10)
framenum = 0

subscreen.write_line("X", (0, 0), 40)
subscreen.write_line("X", (0, 10-1), 40)
subscreen.write_line("X", (0, 0), 10, vertical=True)
subscreen.write_line("X", (40-1, 0), 10, vertical=True)

while True:
	mainscreen.reset()
	mainscreen.write_line(fullblock, (0, 0), termwidth)
	mainscreen.write_line(fullblock, (0, termheight-1), termwidth)
	mainscreen.write_line(fullblock, (0, 0), termheight, vertical=True)
	mainscreen.write_line(fullblock, (termwidth-1, 0), termheight, vertical=True)
	mainscreen.write_array(subscreen, (framenum*4,framenum))
	mainscreen.draw()
	time.sleep(.5)
	framenum += 1
	