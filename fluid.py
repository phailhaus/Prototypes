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

# Initialize world
for simcol in range(simwidth):
	for simrow in range(simheight):
		simcell = simarray[simrow][simcol]
		simcell["blocktype"] = AIR
		simcell["fluidmass"] = 0
		simcell["fluidmassthisframe"] = 0
		simcell["flowx"] = 0
		simcell["flowy"] = 0
		simcell["flowxnew"] = 0
		simcell["flowynew"] = 0
		if simrow == 0 or simrow == simheight - 1: # Create floor/ceiling
			simcell["blocktype"] = GROUND
		elif simcol == 0 or simcol == simwidth - 1: # Create walls
			simcell["blocktype"] = GROUND
		elif simrow == 5 and (simcol != 3 and simcol < 7):
			simcell["blocktype"] = GROUND
		elif simrow <= 4 and simcol == 7:
			simcell["blocktype"] = GROUND
		elif simrow == 10 and simcol >= 12:
			simcell["blocktype"] = GROUND
		elif (simrow == 9 or simrow == 7 or simrow <= 6) and simcol == 12:
			simcell["blocktype"] = GROUND
		elif 18 < simrow < 24 and simcol == 20:
			simcell["blocktype"] = GROUND
		elif (16 < simcol < 20) and simrow == 3:
			simcell["blocktype"] = WATER
			simcell["fluidmass"] = 500
		simarray[simrow][simcol] = simcell

# Water properties
maxmass = 1.0 # The normal, un-pressurized mass of a full water cell
maxcompress = 0.02 # How much excess water a cell can store
minmass = 0.0001  # Ignore cells that are almost dry
flowrate = 0.0 # How much massthisframe is multiplied by each frame, freeing up mass to move.
timescale = 1 # What proportion of full equalization to do each frame
neighborimpact = 0.0 # How much impact the flow of neighbor cells should have
inheritflow = .00 * timescale # How much flow should be passed to the receiving cell

# Sim algorithm loosely based on https://w-shadow.com/blog/2009/09/01/simple-fluid-simulation/. simvertcalc is straight from there, other things are mostly from scratch.
def simvertcalc(uppermass, lowermass):
	totalmass = uppermass + lowermass
	if totalmass <= 1:
		return 1
	elif totalmass < 2*maxmass + maxcompress:
		return (maxmass*maxmass + totalmass*maxcompress) / (maxmass + maxcompress)
	else:
		return (totalmass + maxcompress) / 2

def flowcalc(pressure, flow, neighbor1, neighbor2):
	neighboravg = (neighbor1 + neighbor2) / 2 * neighborimpact
	if neighbor1 != 0 or neighbor2 != 0:
		resultflow = (pressure + flow + neighboravg) / 3
	else:
		resultflow = (pressure + flow) / 2
	resultflow = (pressure + flow) / 2
	return resultflow

def fluidsim(simarray, evenodd = 0):
	# Set block IDs
	AIR = 0
	GROUND = 1
	WATER = 2

	simwidth = len(simarray[0])
	simheight = len(simarray)

	for simrow in range(simheight):
		for simcol in range(simwidth):
			simcell = simarray[simrow][simcol] # This cell

			# if simcol == 6 and simrow == 4:
			# 	simcell["blocktype"] = WATER
			# 	simcell["fluidmass"] = 1
			# 	simcell["fluidmassthisframe"] = 0
			
			if simcell["blocktype"] >= WATER: # Only perform sim if cell is a fluid
				if simcell["fluidmass"] <= minmass: # Turn damp cells into air
					simcell["fluidmass"] = 0
					simcell["blocktype"] = AIR
					simcell["flowx"] = 0
					simcell["flowy"] = 0
					simcell["flowxnew"] = 0
					simcell["flowynew"] = 0
				else:
					cellmass = simcell["fluidmass"]

					# Initialize neighbors as empty cells in case they are out of bounds
					simcellU = {"blocktype": AIR, "fluidmass": 0, "fluidmassthisframe": 0, "flowx": 0, "flowy": 0, "flowxnew": 0, "flowynew": 0}
					simcellD = {"blocktype": AIR, "fluidmass": 0, "fluidmassthisframe": 0, "flowx": 0, "flowy": 0, "flowxnew": 0, "flowynew": 0}
					simcellL = {"blocktype": AIR, "fluidmass": 0, "fluidmassthisframe": 0, "flowx": 0, "flowy": 0, "flowxnew": 0, "flowynew": 0}
					simcellR = {"blocktype": AIR, "fluidmass": 0, "fluidmassthisframe": 0, "flowx": 0, "flowy": 0, "flowxnew": 0, "flowynew": 0}
					
					# Load neighbor data if not out of bounds
					if simrow > 0: # Cell is not on top border
						simcellU = simarray[simrow - 1][simcol]
					if simrow < simheight - 1: # Cell is not on bottom border
						simcellD = simarray[simrow + 1][simcol]
					if simcol > 0: # Cell is not on left border
						simcellL = simarray[simrow][simcol - 1]
					if simcol < simwidth - 1: # Cell is not on right border
						simcellR = simarray[simrow][simcol + 1]
					
					# Falling logic
					downspace = 0
					if simcellD["blocktype"] != GROUND: 
						vertpressure = pygame.math.clamp(simvertcalc(cellmass, simcellD["fluidmass"]) - simcellD["fluidmass"], 0, cellmass - simcell["fluidmassthisframe"])
						flow = flowcalc(vertpressure, simcell["flowy"], simcellU["flowy"], simcellD["flowy"])
						simcell["flowynew"] = (flow + simcell["flowynew"])
						flow = pygame.math.clamp(flow, 0, cellmass - simcell["fluidmassthisframe"])
						simcellD["fluidmass"] += flow * timescale
						simcellD["fluidmassthisframe"] += flow * timescale
						simcellD["flowynew"] += simcell["flowynew"] * inheritflow
						simcellD["flowxnew"] += simcell["flowx"] * inheritflow
						cellmass -= flow * timescale
						
						if simrow < simheight - 1: # Cell is not on bottom border
							simcellD["blocktype"] = WATER
							simarray[simrow + 1][simcol] = simcellD # Write changes to array
						downspace = vertpressure - vertpressure * timescale

					# Spreading logic - Avg with cells on either side that have less. If using evenodd, every other frame.
					if evenodd == 0 or (evenodd == 1 and simcol % 2 == 0) or (evenodd == 2 and simcol % 2 == 1):
						if cellmass > minmass and cellmass > downspace: # Skip if empty or if all fluid can fall
							destmassL = None
							movingL = 0
							destmassR = None
							movingR = 0

							availcellmass = cellmass - downspace

							if simcellL["blocktype"] != GROUND:
								destmassL = simcellL["fluidmass"]
							if simcellR["blocktype"] != GROUND:
								destmassR = simcellR["fluidmass"]

							if (destmassL != None) and (destmassR != None):
								cellmassavg = (destmassL + destmassR + cellmass) / 3
								
								movingL = (cellmassavg - destmassL)
								movingR = (cellmassavg - destmassR)
								
								horpressure = movingR - movingL

								if destmassL == 0 and destmassR == 0:
									randdirection = random.randint(0, 1)
									movingL *= 0 + randdirection
									movingR *= 1 - randdirection
									horpressure = movingR - movingL

								flow = flowcalc(horpressure, simcell["flowx"], simcellL["flowy"], simcellR["flowy"])
								simcell["flowxnew"] = (flow + simcell["flowxnew"])
								flowL = pygame.math.clamp(-flow, 0, cellmass - simcell["fluidmassthisframe"])
								flowR = pygame.math.clamp(flow, 0, cellmass - simcell["fluidmassthisframe"])

								simcellL["fluidmass"] += flowL * timescale
								simcellL["fluidmassthisframe"] += flowL * timescale
								simcellL["flowynew"] += simcell["flowynew"] * inheritflow
								simcellL["flowxnew"] += simcell["flowxnew"] * inheritflow
								cellmass -= flowL * timescale
								
								simcellR["fluidmass"] += flowR * timescale
								simcellR["fluidmassthisframe"] += flowR * timescale
								simcellR["flowynew"] += simcell["flowynew"] * inheritflow
								simcellR["flowxnew"] += simcell["flowxnew"] * inheritflow
								cellmass -= flowR * timescale

							elif destmassL != None:
								cellmassavg = (destmassL + cellmass) / 2
								movingL = (cellmassavg - destmassL)

								horpressure = -movingL
								flow = flowcalc(horpressure, simcell["flowx"], simcellL["flowy"], simcellR["flowy"])
								simcell["flowxnew"] = (flow + simcell["flowxnew"])
								flowL = pygame.math.clamp(-flow, 0, cellmass - simcell["fluidmassthisframe"])

								simcellL["fluidmass"] += flowL * timescale
								simcellL["fluidmassthisframe"] += flowL * timescale
								simcellL["flowynew"] += simcell["flowynew"] * inheritflow
								simcellL["flowxnew"] += simcell["flowxnew"] * inheritflow
								cellmass -= flowL * timescale

							elif destmassR != None:
								cellmassavg = (destmassR + cellmass) / 2
								movingR = (cellmassavg - destmassR)

								horpressure = movingR
								flow = flowcalc(horpressure, simcell["flowx"], simcellL["flowy"], simcellR["flowy"])
								simcell["flowxnew"] = (flow + simcell["flowxnew"])
								flowR = pygame.math.clamp(flow, 0, cellmass - simcell["fluidmassthisframe"])

								simcellR["fluidmass"] += flowR * timescale
								simcellR["fluidmassthisframe"] += flowR * timescale
								simcellR["flowynew"] += simcell["flowynew"] * inheritflow
								simcellR["flowxnew"] += simcell["flowxnew"] * inheritflow
								cellmass -= flowR * timescale
								
							if simcol > 0 and simcellL["fluidmass"] > minmass: # Cell is not on left edge
								simcellL["blocktype"] = WATER
								simarray[simrow][simcol - 1] = simcellL # Write changes to array
							
							if simcol < simwidth - 1 and simcellR["fluidmass"] > minmass: # Cell is not on right edge
								simcellR["blocktype"] = WATER
								simarray[simrow][simcol + 1] = simcellR # Write changes to array
					
					# Upward logic - Push excess mass into cell above.
					if cellmass > maxmass and simcellU["blocktype"] != GROUND:
						availcellmass = cellmass - downspace
						vertpressure = pygame.math.clamp(cellmass - simvertcalc(simcellU["fluidmass"], cellmass),  0, availcellmass - simcell["fluidmassthisframe"])
						flow = flowcalc(-vertpressure, simcell["flowynew"], simcellU["flowy"], simcellD["flowy"])
						simcell["flowynew"] = (flow + simcell["flowynew"])
						flow = pygame.math.clamp(-flow, 0, cellmass - simcell["fluidmassthisframe"])
						simcellU["fluidmass"] += flow * timescale
						simcellU["fluidmassthisframe"] += flow * timescale
						simcellU["flowynew"] += simcell["flowynew"] * inheritflow
						simcellU["flowxnew"] += simcell["flowxnew"] * inheritflow
						cellmass -= flow * timescale

						if simrow > 0: # Cell is not on top edge
							simcellU["blocktype"] = WATER
							simarray[simrow - 1][simcol] = simcellU # Write changes to array

					if cellmass > minmass:
						simcell["fluidmass"] = cellmass
					else: # If cell is now damp, turn into air
						simcell["fluidmass"] = 0 
						simcell["blocktype"] = AIR
				simarray[simrow][simcol] = simcell # Write changes to array
	for simrow in range(simheight):
		for simcol in range(simwidth):
			simarray[simrow][simcol]["fluidmassthisframe"] *= flowrate
			simarray[simrow][simcol]["flowx"] = simarray[simrow][simcol]["flowxnew"]
			simarray[simrow][simcol]["flowxnew"] = 0
			simarray[simrow][simcol]["flowy"] = simarray[simrow][simcol]["flowynew"]
			simarray[simrow][simcol]["flowynew"] = 0
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
			
			# Reset cell
			cellcolor = aircolor 
			cellsurface = pygame.Surface((simscale, simscale))
			simrect = pygame.Rect(simcol * simscale, simrow * simscale, simscale, simscale)
			cellsurface.fill(cellcolor)
			pygame.Surface.blit(simsurface, cellsurface, simrect)
							
			if simcelldata["blocktype"] == GROUND: 
				cellcolor = groundcolor
				cellsurface = pygame.Surface((simscale, simscale))
				simrect = pygame.Rect(simcol * simscale, simrow * simscale, simscale, simscale)
			
			if simcelldata["blocktype"] == WATER:
				if simcelldata["fluidmass"] <= 1:
					cellcolor = watercolor
					cellsize = int(simcelldata["fluidmass"]*simscale)
				else:
					overcolor0 = pygame.math.clamp(int((simcelldata["fluidmass"]-1) * 60), 0, watercolor[0])
					overcolor1 = pygame.math.clamp(int((simcelldata["fluidmass"]-1) * 60), 0, watercolor[1])
					overcolor2 = pygame.math.clamp(int((simcelldata["fluidmass"]-1) * 60), 0, watercolor[2])
					cellcolor = (watercolor[0] - overcolor0, watercolor[1] - overcolor1, watercolor[2] - overcolor2)
					cellsize = simscale
				cellsurface = pygame.Surface((simscale, simscale * cellsize))
				simrect = pygame.Rect(simcol * simscale, (simrow + 1) * simscale - simscale * cellsize / simscale, simscale, simscale * cellsize / simscale)
				cellsurface.set_alpha(int(pygame.math.clamp(simcelldata["fluidmass"] / maxmass * 255, 0, 255)))
			cellsurface.fill(cellcolor)
			pygame.Surface.blit(simsurface, cellsurface, simrect)
			simcol += 1
		simcol = 0
		simrow += 1
	return simsurface

screen = pygame.display.set_mode(screensize) # create window

evenodd = 1

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
		simarray = fluidsim(simarray, 0)
		if evenodd == 1: evenodd = 2
		else: evenodd = 1

		simsurface = simdraw(simarray, simscale)
		pygame.Surface.blit(screen, simsurface, ((screenwidth - (simwidth * simscale)) / 2, (screenheight - (simheight * simscale)) / 2))
		pygame.display.flip()

