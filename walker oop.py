import pygame
from pygame.locals import *
import sys
import random
import time

pygame.init()

screensize = screenwidth, screenheight = 1024, 1024
simsize = simwidth, simheight = 32, 32
simscale = 32

maxmass = 1
timescale = .2
simframerate = 30

# Set material IDs
AIR = 0
GROUND = 1
WATER = 2
BLOOD = 3
HONEY = 4

materialconfig = {
	AIR: {
		"lifespan": 0,
		"flow": 0,
		"color": (200, 220, 255)
	},
	GROUND: {
		"lifespan": 0,
		"flow": 0,
		"color": (64, 128, 32)
	},
	WATER: {
		"lifespan": 6,
		"flow": .55,
		"color": (32, 64, 200)
	},
	BLOOD: {
		"lifespan": 6,
		"flow": .5,
		"color": (180, 30, 30)
	},
	HONEY: {
		"lifespan": 11,
		"flow": .1,
		"color": (210, 180, 50)
	}
}

class Massinput:
	def __init__(self, materialtype, mass, on = False):
		self.materialtype = materialtype
		self.mass = mass
		self.remainingmass = mass
		self.on = on
	
	def dispensemass(self, mass):
		self.remainingmass -= mass
		if self.remainingmass <= 0:
			self.on = False
	
	def reclaimmass(self, mass):
		self.remainingmass += mass
		if self.on == False and self.remainingmass > 0:
			self.on = True
	
	def __str__(self) -> str:
		return f"{self.materialtype}: {self.mass} total mass, {self.remainingmass} remaining mass. On: {self.on}"

class Inputs:
	def __init__(self):
		self.inputlist = list()
	
	def addinput(self, materialtype, mass, on = False):
		self.inputlist.append(Massinput(materialtype, mass, on))

	def giveinput(self, input):
		if type(input) == int:
			return self.inputlist[input]
		else:
			return input
	
	def __str__(self) -> str:
		output = "Inputs:"
		for inputdata in self.inputlist:
			output = f"{output}\n{str(inputdata)}"
		return output

inputlist = Inputs()

inputlist.addinput(GROUND, 0)
inputlist.addinput(WATER, 400, True)
inputlist.addinput(BLOOD, 600, True)
inputlist.addinput(HONEY, 600, True)

class Material:
	def __init__(self, input, mass = 0, newmass = 0):
		self.input = inputlist.giveinput(input)
		self.materialtype = self.input.materialtype
		self.mass = mass
		self.newmass = newmass
	
	def addmass(self, addedmass):
		self.newmass += addedmass
		self.input.dispensemass(addedmass)
	
	def endofframeupdate(self):
		self.mass = self.newmass

class Cell:
	def __init__(self, column, row):
		self.column = column
		self.row = row
		self.materials = list()
		self.inputlist = list()
		self.masstotal = 0
		self.newmasstotal = 0
		self.renderdata = list()
	
	def __str__(self) -> str:
		return f"Cell {self.column}, {self.row}: {self.masstotal}"
	
	def totalmassupdate(self):
		self.masstotal = 0
		self.newmasstotal = 0		
		for material in self.materials:
			self.masstotal += material.mass
			self.newmasstotal += material.newmass

	def addmass(self, input, mass = 0):
		if input in self.inputlist:
			index = self.inputlist.index(input)
			self.materials[index].addmass(mass)
		else:
			self.inputlist.append(input)
			self.materials.append(Material(input, 0, mass))
		self.totalmassupdate()
	
	def endofframeupdate(self):
		self.renderdata = list()
		for material in self.materials:
			material.endofframeupdate()
			cellrenderheight = material.mass / maxmass
			cellrendercolor = materialconfig[material.materialtype]["color"]
			self.renderdata.append((cellrenderheight, cellrendercolor))
		self.totalmassupdate()
	
class Cellarray:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.cellarray = list()

		for column in range(width):
			self.cellarray.append(list())
			for row in range(height):
				self.cellarray[column].append(Cell(column, row))
	
	def cellarrayprint(self, column = None, row = None):
		output = ""
		r = 0
		while r < self.height:
			if row == None or r == row:
				c = 0
				while c < self.width:
					if column == None or c == column:
						output = f"{output} | {str(self.cellarray[c][r])}"
					c += 1
				output = f"{output} |\n"
			r += 1
		return output

	def placeinput(self, column, row, input):
		self.cellarray[column][row].addmass(input, maxmass - self.cellarray[column][row].newmasstotal)
	
	def neighbors(self, column = None, row = None):
		output = list()
		if row > 0:	output.append(self.cellarray[column][row - 1]) # Up
		if column < simwidth - 2: output.append(self.cellarray[column + 1][row]) # Right
		if row < simheight - 2: output.append(self.cellarray[column][row + 1]) # Down
		if column > 0: output.append(self.cellarray[column - 1][row]) # Left
		return output
	
	def endofframeupdate(self):
		for row in self.cellarray:
			for cell in row:
				cell.endofframeupdate()
	
	def simupdate(self):
		for row in self.cellarray:
			for cell in row:
				if len(cell.materials) > 0 and cell.masstotal >= maxmass:
					for flowingmaterial in sorted(cell.materials, key=lambda elem: elem.mass, reverse=True): # Iterates through the materials on the current cell in decending order.
						if flowingmaterial.input.on:
							neighbors = self.neighbors(cell.column, cell.row)
							massneededtofill = 0
							massneededlist = list()
							cellsneedingmass = 0
							materialmaxflow = pygame.math.clamp((flowingmaterial.mass / maxmass), 0, 1) * materialconfig[flowingmaterial.materialtype]["flow"] * timescale # Portion of the cell that is this material times flow rate times timescale
							for neighbor in neighbors:
								if neighbor.newmasstotal >= maxmass:
									massneededlist.append(0)
								else:
									if maxmass - neighbor.newmasstotal >= materialmaxflow:
										massneededtofill += materialmaxflow
										massneededlist.append(materialmaxflow)
									else:
										massneededtofill += maxmass - neighbor.newmasstotal
										massneededlist.append(maxmass - neighbor.newmasstotal)
									cellsneedingmass += 1
							if massneededtofill > flowingmaterial.input.remainingmass: # Reduce outgoing mass to below remaining mass
								materialmaxflow = flowingmaterial.input.remainingmass / cellsneedingmass
								massneededlistnew = list()
								for massneeded in massneededlist:
									if massneeded <= materialmaxflow:
										massneededlistnew.append(massneeded)
									else:
										massneededlistnew.append(materialmaxflow)
								massneededlist = list(massneededlistnew)
								del massneededlistnew
							for neighborindex in range(len(massneededlist)):
								if len(massneededlist) > 0:
									neighbors[neighborindex].addmass(flowingmaterial.input, massneededlist[neighborindex])
		self.endofframeupdate()
	
	def __str__(self) -> str:
		return f"{self.width} x {self.height} array:\n{self.cellarrayprint()}"


def simdraw(simarray, simscale): # iterates through a given 2D array, drawing the contents to a surface
	simwidth = simarray.width
	simheight = simarray.height
	simsurface = pygame.Surface((simwidth * simscale, simheight * simscale))
	simsurface.fill(materialconfig[AIR]["color"])
	simrow = 0
	simcol = 0
	for simcolumnarray in simarray.cellarray:
		for simcelldata in simcolumnarray:
			if len(simcelldata.renderdata) > 0:
				cumulativesize = 0
				for renderdata in sorted(simcelldata.renderdata, key=lambda elem: elem[0], reverse=True): # Iterates through the target dict in decending order sorted by the listed subkey.
					cellcolor = renderdata[1]
					cellsize = int(renderdata[0] * simscale)
					cumulativesize += cellsize
					
					cellsurface = pygame.Surface((simscale, cellsize))
					simrect = pygame.Rect(simcol * simscale, (simrow + 1) * simscale - cumulativesize, simscale, simscale * cellsize)
					#cellsurface.set_alpha(int(pygame.math.clamp(flowingmaterialdata["fluidmass"] / maxmass * 255, 0, 255)))
					cellsurface.fill(cellcolor)
					pygame.Surface.blit(simsurface, cellsurface, simrect)
			simrow += 1
		simrow = 0
		simcol += 1
	return simsurface

screen = pygame.display.set_mode(screensize) # create window

simarray = Cellarray(simwidth, simheight)

for simcol in range(simwidth):
	for simrow in range(simheight):
		if simrow == 0 or simrow == simheight - 1: # Create floor/ceiling
			simarray.placeinput(simcol, simrow, 0)
		elif simcol == 0 or simcol == simwidth - 1: # Create walls
			simarray.placeinput(simcol, simrow, 0)
		elif simrow == 5 and (simcol != 3 and simcol < 7):
			simarray.placeinput(simcol, simrow, 0)
		elif simrow <= 4 and simcol == 7:
			simarray.placeinput(simcol, simrow, 0)
		elif simrow == 10 and simcol >= 12:
			simarray.placeinput(simcol, simrow, 0)
		elif (simrow == 9 or simrow == 7 or simrow <= 6) and simcol == 12:
			simarray.placeinput(simcol, simrow, 0)
		elif 18 < simrow < 24 and simcol == 20:
			simarray.placeinput(simcol, simrow, 0)
		elif (simcol == 18) and (simrow == 3):
			simarray.placeinput(simcol, simrow, 2)
		elif (simcol == 4) and simrow == 3:
			simarray.placeinput(simcol, simrow, 1)
		elif (simcol == 14) and (simrow == 11 or simrow == 16):
			simarray.placeinput(simcol, simrow, 3)

frame_cap = 1.0/simframerate
time_1 = time.perf_counter()
unprocessed = 0

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
	
	can_render = False
	time_2 = time.perf_counter()
	passed = time_2 - time_1
	unprocessed += passed
	time_1 = time_2

	while(unprocessed >= frame_cap):
		unprocessed -= frame_cap
		can_render = True
	
	if can_render:
		simarray.simupdate()
		simsurface = simdraw(simarray, simscale)
		pygame.Surface.blit(screen, simsurface, ((screenwidth - (simwidth * simscale)) / 2, (screenheight - (simheight * simscale)) / 2))
		pygame.display.flip()