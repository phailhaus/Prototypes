import math
import random
import sys

import pygame
from pygame.locals import *
import pygame.freetype

import terminalUI as tui
import settlementGenerator as sg

perfmanager = sg.perfAnnouncer()
perfmanager.announce("Startup")

pygame.init()

clock = pygame.time.Clock()

termwidth = 50
termheight = 50

framerate = 60

#font = pygame.freetype.Font("freefont-20120503\FreeMono.otf", 16)
#font.strong = True
fontsize = (16, 16) # Pygame window is (termwidth * fontsize[0], termheight * fontsize[1]). 
tui.fontsize = fontsize

#tui.setfont(font, fontsize)

screenwidth, screenheight = termwidth * fontsize[0], termheight * fontsize[1]

newline = chr(10)
blank = " "
fullblock = chr(9608)

sim_grid = sg.Grid(termwidth, termheight)

perfmanager.announce("Grid creation")

def add_color_emitters(sim_grid, count, radius, power, falloff_function):
	perfmanager.record()
	for stat in ("r", "g", "b"):
		for i in range(count):
			rand_x = random.randint(0, termwidth-1)
			rand_y = random.randint(0, termheight-1)
			sim_grid.get_cell(rand_x, rand_y).add_emitter(radius = radius, stat_name = stat, power = power, falloff_function = falloff_function)

	sim_grid.run_emitters()
	perfmanager.announce("Emitter running")

def remove_emitters(sim_grid):
	for gridcell in sim_grid.array_flat:
		gridcell.emitters = list()
		gridcell.reset_input()

def change_radius(sim_grid, new_radius):
	recalculated_targets = list()
	for gridcell in sim_grid.array_flat:
		for emitter in gridcell.emitters:
			recalculated_targets.extend(emitter.change_radius(emitter_radius, recalculate = False))
	recalculated_targets = list(set(recalculated_targets))
	for target in recalculated_targets:
		if target != None:
			target.calculate_stats()


emitter_radius = 15
add_color_emitters(sim_grid, count = 10, radius = emitter_radius, power = 100, falloff_function = sg.Falloff_functions.quintic_hermite)

def main():
	pygameScreen = pygame.display.set_mode((termwidth * fontsize[0], termheight * fontsize[1]))
	mainscreen = tui.textSurface(termwidth, termheight)

	framenum = 0
	global emitter_radius

	while True:
		for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit(0)
					elif event.type == pygame.KEYDOWN:
						if event.key == pygame.K_ESCAPE: sys.exit(0)
						if event.key == pygame.K_r: remove_emitters(sim_grid)
						if event.key == pygame.K_SPACE:
							add_color_emitters(sim_grid, count = 1, radius = emitter_radius, power = 100, falloff_function = sg.Falloff_functions.quintic_hermite)
						if event.key == pygame.K_UP:
							emitter_radius += 1
							change_radius(sim_grid, emitter_radius)
						if event.key == pygame.K_DOWN:
							if emitter_radius >= 1:
								emitter_radius -= 1
								change_radius(sim_grid, emitter_radius)

						
		
		# keyspressed = pygame.key.get_pressed()
		# if keyspressed[K_SPACE]: pass

		mainscreen.reset()
		for gridcell in sim_grid.array_flat:
			if len(gridcell.emitters) > 0:
				drawchar = "."
			else:
				drawchar = blank
			r, g, b = 0, 0, 0
			stats = gridcell.stats
			if len(stats) > 0:
				if "r" in stats:
					r = min(stats["r"], 255)
				if "g" in stats:
					g = min(stats["g"], 255)
				if "b" in stats:
					b = min(stats["b"], 255)
			if max(r, g, b) > 0 or drawchar != blank:
				mainscreen.write_single(drawchar, (gridcell.pos_x, gridcell.pos_y), (255, 255, 255), (r, g, b))

		pygameScreen.fill((0, 0, 0))
		mainscreen.drawPygame(pygameScreen)
		pygame.display.flip()
		

		#time.sleep(1/framerate)
		clock.tick(framerate)
		#print(clock.get_fps())
		framenum += 1

if __name__ == '__main__':
	sys.exit(main())