import pygame
from pygame.locals import *
import sys
import random
import time

pygame.init()

screensize = screenwidth, screenheight = 512, 512
simsize = simwidth, simheight = 32, 32
simscale = 16

aircolor = 200, 220, 255
groundcolor = 64, 128, 32

# Set material IDs
AIR = 0
GROUND = 1
WATER = 2
BLOOD = 3
HONEY = 4

simarray = [[{} for i in range(simwidth)] for j in range(simheight)] # Create sim array

fluidconfig = {
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
		"flow": .5,
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

inputs = list()
inputs.append({"type": WATER, "on": True, "totalvolume": 400, "remainingvolume": 400})
inputs.append({"type": BLOOD, "on": True, "totalvolume": 600, "remainingvolume": 600})
inputs.append({"type": HONEY, "on": True, "totalvolume": 600, "remainingvolume": 600})

# Initialize world
aircell = {
	"blocktype": AIR,
	"blocktypenew": AIR,
	"fluidmass": 0,
	"fluidmassnew": 0,
	"flowx": 0,
	"flowy": 0,
	"flowxnew": 0,
	"flowynew": 0,
	"lifespan": 0,
	"input": None
}
groundcell = {
	"blocktype": GROUND,
	"blocktypenew": GROUND,
	"fluidmass": 1,
	"fluidmassnew": 1,
	"flowx": 0,
	"flowy": 0,
	"flowxnew": 0,
	"flowynew": 0,
	"lifespan": 0,
	"input": None
}

for simcol in range(simwidth):
	for simrow in range(simheight):
		simcell = dict(aircell)
		if simrow == 0 or simrow == simheight - 1: # Create floor/ceiling
			simcell = dict(groundcell)
		elif simcol == 0 or simcol == simwidth - 1: # Create walls
			simcell = dict(groundcell)
		elif simrow == 5 and (simcol != 3 and simcol < 7):
			simcell = dict(groundcell)
		elif simrow <= 4 and simcol == 7:
			simcell = dict(groundcell)
		elif simrow == 10 and simcol >= 12:
			simcell = dict(groundcell)
		elif (simrow == 9 or simrow == 7 or simrow <= 6) and simcol == 12:
			simcell = dict(groundcell)
		elif 18 < simrow < 24 and simcol == 20:
			simcell = dict(groundcell)
		elif (simcol == 18) and (simrow == 3):
			simcell["input"] = 1
		elif (simcol == 4) and simrow == 3:
			simcell["input"] = 0
		elif (simcol == 18) and (simrow == 11 or simrow == 16):
			simcell["input"] = 2
		simarray[simrow][simcol] = simcell

# Water properties
maxmass = 1.0 # The normal, un-pressurized mass of a full water cell
timescale = .5 # What proportion of full equalization to do each frame

def flowcalc(materialmaxflow, remainingvolume, targetmass, cellsneedingmass):
	if materialmaxflow * cellsneedingmass > remainingvolume: # Cap flow at remaining mass divided by available targets for this cell
		maxflow = remainingvolume / cellsneedingmass
	else:
		maxflow = materialmaxflow

	neededmass = maxmass - targetmass
	if neededmass > maxflow: # Cap needed mass at flow
		neededmass = maxflow
	return neededmass
	

def simlogic(coordrow, coordcol, simarray):
	thiscell = simarray[coordrow][coordcol]
	targetcelltuple = (simarray[coordrow - 1][coordcol], simarray[coordrow][coordcol + 1], simarray[coordrow + 1][coordcol], simarray[coordrow][coordcol - 1]) # 0: U. 1: R. 2: D. 3: L
	massneededtofill = 0
	fluidmasslist = list()
	cellsneedingmass = 0
	materialmaxflow = fluidconfig[thiscell["blocktype"]]["flow"] * timescale
	for targetcell in targetcelltuple:
		if targetcell["blocktypenew"] == AIR or targetcell["blocktypenew"] == thiscell["blocktype"]:
			if maxmass - targetcell["fluidmassnew"] >= materialmaxflow:
				massneededtofill += materialmaxflow
			else:
				massneededtofill += maxmass - targetcell["fluidmassnew"]
			fluidmasslist.append(targetcell["fluidmassnew"])
			cellsneedingmass += 1
		else:
			fluidmasslist.append(maxmass)
	massinput = inputs[thiscell["input"]]
	flowlist = list()
	if massneededtofill > 0 and massinput["remainingvolume"] > 0:
		for cellid in range(len(fluidmasslist)):
			if fluidmasslist[cellid] < maxmass:
				flowlist.append(flowcalc(materialmaxflow, massinput["remainingvolume"], fluidmasslist[cellid], cellsneedingmass))
			else: flowlist.append(0)
	for cellid in range(len(flowlist)):
		if flowlist[cellid] > 0:
			targetcelltuple[cellid]["fluidmassnew"] = targetcelltuple[cellid]["fluidmassnew"] + flowlist[cellid]
			targetcelltuple[cellid]["blocktypenew"] = thiscell["blocktype"]
			targetcelltuple[cellid]["input"] = thiscell["input"]
			inputs[thiscell["input"]]["remainingvolume"] -= flowlist[cellid]

		
	simarray[coordrow - 1][coordcol] = targetcelltuple[0]
	simarray[coordrow][coordcol + 1] = targetcelltuple[1]
	simarray[coordrow + 1][coordcol] = targetcelltuple[2]
	simarray[coordrow][coordcol - 1] = targetcelltuple[3]

	return simarray

def simcore(simarray):

	simwidth = len(simarray[0])
	simheight = len(simarray)
	fluidsum = 0

	for simrow in range(simheight):
		for simcol in range(simwidth):
			simcell = simarray[simrow][simcol] # This cell
			
			if simcell["input"] != None:
				fluidsum += simcell["fluidmass"]

			if simcell["input"] != None and simcell["blocktypenew"] == AIR and inputs[simcell["input"]]["on"] and inputs[simcell["input"]]["remainingvolume"] >= maxmass:
				simcell["fluidmass"] = maxmass
				simcell["fluidmassnew"] = maxmass
				simcell["blocktype"] = inputs[simcell["input"]]["type"]
				simcell["blocktypenew"] = inputs[simcell["input"]]["type"]
				inputs[simcell["input"]]["remainingvolume"] -= maxmass
				

			if simcell["blocktype"] > GROUND and simcell["fluidmass"] >= maxmass and inputs[simcell["input"]]["on"] and simcell["lifespan"] <= fluidconfig[simcell["blocktype"]]["lifespan"] : # Only perform sim if cell is a fluid and not dead
				simarray = simlogic(simrow, simcol, simarray)
				simcell["lifespan"] += 1 * timescale
				
	for simrow in range(simheight):
		for simcol in range(simwidth):
			simarray[simrow][simcol]["blocktype"] = simarray[simrow][simcol]["blocktypenew"]
			simarray[simrow][simcol]["fluidmass"] = simarray[simrow][simcol]["fluidmassnew"]
	for inputid in range(len(inputs)-1):
		if inputs[inputid]["remainingvolume"] == 0:
			inputs[inputid]["on"] == False
	print(fluidsum)
	return simarray

							
def simdraw(simarray, simscale): # iterates through a given 2D array, drawing the contents to a surface
	simwidth = len(simarray[0])
	simheight = len(simarray)	
	simsurface = pygame.Surface((simwidth * simscale, simheight * simscale))
	simsurface.fill(fluidconfig[AIR]["color"])
	simrow = 0
	simcol = 0
	for simrowarray in simarray:
		for simcelldata in simrowarray:
			cellcolor = fluidconfig[simcelldata["blocktype"]]["color"]
			cellsize = int(simcelldata["fluidmass"] / maxmass * simscale)
			
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

