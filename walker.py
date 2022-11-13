import pygame
from pygame.locals import *
import sys
import random
import time

pygame.init()

screensize = screenwidth, screenheight = 1024, 1024
simsize = simwidth, simheight = 32, 32
simscale = 32

aircolor = 200, 220, 255
groundcolor = 64, 128, 32
watercolor = 32, 64, 200

# Set block IDs
AIR = 0
GROUND = 1
WATER = 2

simarray = [[{} for i in range(simwidth)] for j in range(simheight)] # Create sim array

fluidconfig = {
	WATER: {
		"lifespan": 6,
		"velocity": .2
	}
}

# Initialize world
for simcol in range(simwidth):
	for simrow in range(simheight):
		simcell = simarray[simrow][simcol]
		simcell["blocktype"] = AIR
		simcell["blocktypenew"] = AIR
		simcell["fluidmass"] = 0
		simcell["fluidmassnew"] = 0
		simcell["flowx"] = 0
		simcell["flowy"] = 0
		simcell["flowxnew"] = 0
		simcell["flowynew"] = 0
		simcell["lifespan"] = 0
		if simrow == 0 or simrow == simheight - 1: # Create floor/ceiling
			simcell["blocktype"] = GROUND
			simcell["blocktypenew"] = GROUND
		elif simcol == 0 or simcol == simwidth - 1: # Create walls
			simcell["blocktype"] = GROUND
			simcell["blocktypenew"] = GROUND
		elif simrow == 5 and (simcol != 3 and simcol < 7):
			simcell["blocktype"] = GROUND
			simcell["blocktypenew"] = GROUND
		elif simrow <= 4 and simcol == 7:
			simcell["blocktype"] = GROUND
			simcell["blocktypenew"] = GROUND
		elif simrow == 10 and simcol >= 12:
			simcell["blocktype"] = GROUND
			simcell["blocktypenew"] = GROUND
		elif (simrow == 9 or simrow == 7 or simrow <= 6) and simcol == 12:
			simcell["blocktype"] = GROUND
			simcell["blocktypenew"] = GROUND
		elif 18 < simrow < 24 and simcol == 20:
			simcell["blocktype"] = GROUND
			simcell["blocktypenew"] = GROUND
		elif (16 < simcol < 20) and simrow == 3:
			simcell["blocktype"] = WATER
			simcell["blocktypenew"] = WATER
			simcell["fluidmass"] = 1
			simcell["fluidmassnew"] = 1
		simarray[simrow][simcol] = simcell

# Water properties
maxmass = 1.0 # The normal, un-pressurized mass of a full water cell
timescale = .5 # What proportion of full equalization to do each frame

def simlogic(simcell, targetcell):
	if targetcell["fluidmass"] < 1 and targetcell["blocktype"] != GROUND:
		targetcell["blocktypenew"] = simcell["blocktype"]
		targetcell["fluidmassnew"] = targetcell["fluidmassnew"] + 1 * fluidconfig[simcell["blocktype"]]["velocity"] * timescale
		if targetcell["fluidmassnew"] > 1:
			targetcell["fluidmassnew"] = 1
	return simcell, targetcell

def simcore(simarray):

	simwidth = len(simarray[0])
	simheight = len(simarray)

	for simrow in range(simheight):
		for simcol in range(simwidth):
			simcell = simarray[simrow][simcol] # This cell
			if simcell["fluidmass"] >= 1 and simcell["lifespan"] <= fluidconfig[simcell["blocktype"]]["lifespan"] : # Only perform sim if cell is a fluid and not dead
				# Load neighbor data if not out of bounds
				if simrow > 0: # Cell is not on top border
					targetcell = simarray[simrow - 1][simcol]
					simcell, simarray[simrow - 1][simcol] = simlogic(simcell, targetcell)
				if simrow < simheight - 1: # Cell is not on bottom border
					targetcell = simarray[simrow + 1][simcol]
					simcell, simarray[simrow + 1][simcol] = simlogic(simcell, targetcell)
				if simcol > 0: # Cell is not on left border
					targetcell = simarray[simrow][simcol - 1]
					simcell, simarray[simrow][simcol - 1] = simlogic(simcell, targetcell)
				if simcol < simwidth - 1: # Cell is not on right border
					targetcell = simarray[simrow][simcol + 1]
					simcell, simarray[simrow][simcol + 1] = simlogic(simcell, targetcell)
				simcell["lifespan"] += 1 * timescale
				
	for simrow in range(simheight):
		for simcol in range(simwidth):
			simarray[simrow][simcol]["blocktype"] = simarray[simrow][simcol]["blocktypenew"]
			simarray[simrow][simcol]["fluidmass"] = simarray[simrow][simcol]["fluidmassnew"]
	return simarray

							
def simdraw(simarray, simscale): # iterates through a given 2D array, drawing the contents to a surface
	simwidth = len(simarray[0])
	simheight = len(simarray)	
	simsurface = pygame.Surface((simwidth * simscale, simheight * simscale))
	simsurface.fill(aircolor)
	simrow = 0
	simcol = 0
	for simrowarray in simarray:
		for simcelldata in simrowarray:
						
			if simcelldata["blocktype"] == GROUND: 
				cellcolor = groundcolor
				cellsurface = pygame.Surface((simscale, simscale))
				simrect = pygame.Rect(simcol * simscale, simrow * simscale, simscale, simscale)
			
			if simcelldata["blocktype"] == WATER:
				if simcelldata["fluidmass"] < 1:
					cellcolor = watercolor
					cellsize = int(simcelldata["fluidmass"]*simscale)
				else:
					overcolor0 = pygame.math.clamp(int((simcelldata["fluidmass"]-1) * 60), 0, watercolor[0])
					overcolor1 = pygame.math.clamp(int((simcelldata["fluidmass"]-1) * 60), 0, watercolor[1])
					overcolor2 = pygame.math.clamp(int((simcelldata["fluidmass"]-1) * 60), 0, watercolor[2])
					cellcolor = (watercolor[0] - overcolor0, watercolor[1] - overcolor1, watercolor[2] - overcolor2)
					cellsize = simscale
				cellsurface = pygame.Surface((simscale, cellsize))
				simrect = pygame.Rect(simcol * simscale, (simrow + 1) * simscale - cellsize, simscale, simscale * cellsize)
				cellsurface.set_alpha(int(pygame.math.clamp(simcelldata["fluidmass"] / maxmass * 255, 0, 255)))
			cellsurface.fill(cellcolor)
			pygame.Surface.blit(simsurface, cellsurface, simrect)
			simcol += 1
		simcol = 0
		simrow += 1
	return simsurface

screen = pygame.display.set_mode(screensize) # create window

frame_cap = 1.0/30
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
		simarray = simcore(simarray)
		
		simsurface = simdraw(simarray, simscale)
		pygame.Surface.blit(screen, simsurface, ((screenwidth - (simwidth * simscale)) / 2, (screenheight - (simheight * simscale)) / 2))
		pygame.display.flip()

