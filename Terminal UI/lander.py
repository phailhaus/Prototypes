import os
import sys
import time
import math
import pygame
from pygame.locals import *
import pygame.freetype
import terminalUI
import pymunk
import pymunk.pygame_util

pygame.init()

termwidth = 120
termheight = 60

framerate = 60

#font = pygame.freetype.Font("freefont-20120503\FreeMono.otf", 16)
#font.strong = True
fontsize = terminalUI.fontsize # Pygame window is (termwidth * fontsize[0], termheight * fontsize[1]). 

#terminalUI.setfont(font, fontsize)

screenwidth, screenheight = termwidth * fontsize[0], termheight * fontsize [1]

newline = chr(10)
blank = " "
fullblock = chr(9608)
lowerhalfblock = chr(9604)
triangles = str( # Eight directions starting from up and going clockwise
	chr(9650) +
	chr(9701) +
	chr(9654) +
	chr(9698) +
	chr(9660) +
	chr(9699) +
	chr(9664) +
	chr(9700)
)

def add_environment(space):
	body = pymunk.Body(body_type = pymunk.Body.STATIC)
	body.position = (screenwidth/2, screenheight/2)
	lines = []
	lines.append(pymunk.Segment(body, (-(screenwidth/2) + 50, (screenheight/2) - 50), ((screenwidth/2) - 50, (screenheight/2) - 50), 10)) # Bottom
	
	space.add(body)
	
	for line in lines:
		space.add(line)

	return lines

def write_lines(screen, lines, symbol, fgcolor=None, bgcolor=None):
	for line in lines:
		body = line.body
		startingpoint = body.position + line.a.rotated(body.angle)
		startingpoint = (startingpoint[0]/fontsize[0], startingpoint[1]/fontsize[1])
		endingpoint = body.position + line.b.rotated(body.angle)
		endingpoint = (endingpoint[0]/fontsize[0], endingpoint[1]/fontsize[1])
		linevector = pymunk.Vec2d((endingpoint[0]-startingpoint[0]),(endingpoint[1]-startingpoint[1]))
		screen.write_line(symbol, linevector.length, startingpoint, angle=linevector.angle_degrees, fgcolor=fgcolor, bgcolor=bgcolor)
	
def write_lander(screen, lander, fgcolor=None, bgcolor=None):
	landerangle = math.degrees(lander.body.angle)
	symbol = triangles[round(landerangle/45) % 8]
	landerposition = lander.body.position
	landerposition = (round(landerposition[0]/fontsize[0]), round(landerposition[1]/fontsize[1]))
	for v in lander.get_vertices():
		x,y = v.rotated(lander.body.angle) + lander.body.position
		vertex = (round(x/fontsize[0]), round(y/fontsize[1]))
		screen.write_single(symbol, vertex, fgcolor=fgcolor, bgcolor=bgcolor)
	screen.write_single(symbol, landerposition, fgcolor=fgcolor, bgcolor=bgcolor)
	screen.write_string(str(round(landerangle)), (2,2))

def write_landerstats(screen, lander):
	landerangle = math.degrees(lander.body.angle)
	landerav = math.degrees(lander.body.angular_velocity)
	landervel = lander.body.velocity
	line = 1
	screen.write_string(f"Angle: {round(landerangle)}{chr(176)}", (2,line))
	line += 1
	screen.write_string(f"A Vel: {round(landerav)}/sec", (2,line))
	line += 1
	screen.write_string(f"X Vel: {round(landervel[0])}", (2,line))
	line += 1
	screen.write_string(f"Y Vel: {round(landervel[1])}", (2,line))

	

def main():
	pygameScreen = pygame.display.set_mode((termwidth * fontsize[0], termheight * fontsize[1]))
	mainscreen = terminalUI.textSurface(termwidth, termheight)
	uiscreen = terminalUI.textSurface(20, 7, defaultfgcolor = (100, 255, 100), defaultbgcolor = (30, 80, 30))
	space = pymunk.Space()
	space.gravity = (0.0, 200.0)
	lines = add_environment(space)
	landerbody = pymunk.Body()
	lander = pymunk.Poly.create_box(body=landerbody, size=(fontsize[0] * 4, fontsize[1] * 4), radius=1)
	lander.density = 1
	space.add(landerbody, lander)
	landerbody.position = (screenwidth/2, 10)

	framenum = 0

	while True:
		for event in pygame.event.get():
					if event.type == pygame.QUIT:
						sys.exit(0)
					elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
						sys.exit(0)
		
		keyspressed = pygame.key.get_pressed()
		if keyspressed[K_UP] or keyspressed[K_KP8]: landerbody.apply_force_at_local_point((0,-600 * landerbody.mass))
		if keyspressed[K_KP7]: landerbody.apply_force_at_local_point((-600 * landerbody.mass, 0))
		if keyspressed[K_KP9]: landerbody.apply_force_at_local_point((600 * landerbody.mass, 0))
		if keyspressed[K_LEFT] or keyspressed[K_KP4]: landerbody.angular_velocity -= .01
		if keyspressed[K_RIGHT] or keyspressed[K_KP6]: landerbody.angular_velocity += .01

		space.step(1/framerate)
		mainscreen.reset()
		uiscreen.reset()
		mainscreen.write_rectangle(fullblock, (0, 0), termwidth, termheight, fgcolor = (100, 255, 100), bgcolor = (30, 80, 30))
		uiscreen.write_rectangle(fullblock, (0, 0), uiscreen.width, uiscreen.height)
		write_lines(mainscreen, lines, fullblock)
		write_lander(mainscreen, lander)
		write_landerstats(uiscreen, lander)
		mainscreen.write_surface(uiscreen, (0,0))

		pygameScreen.fill((0, 0, 0))
		mainscreen.drawPygame(pygameScreen)
		pygame.display.flip()
		

		time.sleep(1/framerate)
		framenum += 1

if __name__ == '__main__':
	sys.exit(main())