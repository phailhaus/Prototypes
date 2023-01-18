import pygame
import pygame.gfxdraw
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import threading
import sys
import random
import time
import csv
import numpy as np

pygame.init()

screensize = screenwidth, screenheight = 1024, 1024
cellsize = 32
minballsincell = 12 # Add blanks to cells with less balls than this
cellsbrightness = 1
framerate = 60

collisionTypes = dict()
collisionTypes["environment"] = 0
collisionTypes["ball"] = 1

def objimport(file):
	start = None
	last = None
	this = None
	output = list()
	with open(file, newline="") as csvfile:
		csvreader = csv.reader(csvfile, delimiter=" ")
		for row in csvreader:
			if len(row) > 0:
				if row[0] == "v":
					this = (int(float(row[1])), -int(float(row[2])))
					if last == None:
						start = this
					else:
						output.append((last, this)) # Write line segments
					last = this
	output.append((this, start)) # Write final segment to close shape
	return output

				


def add_ball(space, posx, posy):
	posx, posy = int(posx), int(posy)
	mass = 1
	radius = 8
	jitter = 5
	body = pymunk.Body()
	x = random.randint(posx-jitter, posx+jitter)
	y = random.randint(posy-jitter, posy+jitter)
	body.position = x, y
	shape = pymunk.Circle(body, radius)
	shape.collision_type = collisionTypes["ball"]
	shape.mass = mass
	shape.friction = .5
	shape.elasticity = .5
	space.add(body, shape)
	return shape, body

def switch_ball(arbiter, space, data):
	switchodds = 1/100
	randomnumber = random.random()
	if randomnumber <= switchodds:
		ball0, ball1 = arbiter.shapes
		ball0.body.position, ball1.body.position = ball1.body.position, ball0.body.position # Invert positions to emulate diffusion
		ball0.body.velocity, ball1.body.velocity = ball1.body.velocity, ball0.body.velocity # Invert velocities to emulate diffusion
	return True



def draw_balls(screen, balls, color):
	#mappedcolor = screen.map_rgb(color)
	for ball in balls:
		p = int(ball.body.position.x), int(ball.body.position.y)
		x = p[0]
		y = p[1]
		pygame.gfxdraw.pixel(screen, x, y, color)
		# pixelarray[(x,y)] = mappedcolor
		# pixelarray[(x-1,y)] = mappedcolor
		# pixelarray[(x,y-1)] = mappedcolor
		# pixelarray[(x,y)] = mappedcolor
		# pixelarray[(x,y+1)] = mappedcolor
		# pixelarray[(x+1,y)] = mappedcolor
	#return pixelarray
		#pygame.draw.circle(screen, color, p, int(ball.radius), 1)
		#pygame.gfxdraw.pixel(screen, p[0], p[1], color)

def draw_balls_cells(cellarray, cellsize, balls, color):
	for ball in balls:
		p = int(ball.body.position.x), int(ball.body.position.y)
		x = int(p[0]/cellsize)
		y = int(p[1]/cellsize)
		thisballvalues = np.array((color[0], color[1], color[2], 1), dtype = np.int16)
		cellarray[x,y] = cellarray[x, y] + thisballvalues

def draw_cell_array(outputsurface, cellarray):
	width, height, depth = np.shape(cellarray)
	tempsurface = pygame.Surface((width, height))
	pixelarray = np.empty((width, height))
	for x in range(width):
		for y in range(height):
			if cellarray[x, y, 3] > minballsincell:
				ballsincell = cellarray[x, y, 3]
			else:
				ballsincell = minballsincell
			color = (cellarray[x, y, 0]/ballsincell*cellsbrightness, cellarray[x, y, 1]/ballsincell*cellsbrightness, cellarray[x, y, 2]/ballsincell*cellsbrightness)
			pixelarray[x, y] = tempsurface.map_rgb(color)
			
			#pygame.gfxdraw.pixel(tempsurface, x, y, (cellarray[x, y, 0]/ballsincell/2, cellarray[x, y, 1]/ballsincell/2, cellarray[x, y, 2]/ballsincell/2))
	pygame.surfarray.blit_array(tempsurface, pixelarray)
	tempsurfaceX2 = pygame.transform.scale2x(tempsurface)
	tempsurfaceX4 = pygame.transform.scale2x(tempsurfaceX2)
	pygame.transform.scale(tempsurfaceX4, screensize, outputsurface)




def add_environment(space):
	body = pymunk.Body(body_type = pymunk.Body.STATIC)
	body.position = (screenwidth/2, screenheight/2)
	lines = []
	lines.append(pymunk.Segment(body, (-(screenwidth/2) + 10, -(screenheight/2) + 10), ((screenwidth/2) - 10, -(screenheight/2) + 10), 10)) # Top
	lines.append(pymunk.Segment(body, (-(screenwidth/2) + 10, (screenheight/2) - 10), ((screenwidth/2) - 10, (screenheight/2) - 10), 10)) # Bottom
	lines.append(pymunk.Segment(body, (-(screenwidth/2) + 10, -(screenheight/2) + 10), (-(screenwidth/2) + 10, (screenheight/2) - 10), 10)) # Left
	lines.append(pymunk.Segment(body, ((screenwidth/2) - 10, -(screenheight/2) + 10), ((screenwidth/2) - 10, (screenheight/2) - 10), 10)) # Right

	importlines = objimport(r"apple.obj")
	for importline in importlines:
		lines.append(pymunk.Segment(body, importline[0], importline[1], 10))
	importlines = objimport(r"appleAouter.obj")
	for importline in importlines:
		lines.append(pymunk.Segment(body, importline[0], importline[1], 10))
	importlines = objimport(r"appleAinner.obj")
	for importline in importlines:
		lines.append(pymunk.Segment(body, importline[0], importline[1], 10))


	for line in lines:
		line.friction = .5
		line.collision_type = collisionTypes["environment"]
	
	space.add(body)
	
	for line in lines:
		space.add(line)

	return lines

def draw_lines(screen, lines):
	for line in lines:
		body = line.body
		pv1 = body.position + line.a.rotated(body.angle)
		pv2 = body.position + line.b.rotated(body.angle)
		p1 = to_pygame(pv1)
		p2 = to_pygame(pv2)
		pygame.draw.lines(screen, (125,125,125), False, [p1,p2], 5)

def to_pygame(p):
	return round(p.x), round(p.y)

def main():
	pygame.init()
	screen = pygame.display.set_mode((screenwidth, screenheight))
	pygame.display.set_caption("Particle Sim")
	clock = pygame.time.Clock()
	perfstart = time.perf_counter()
	perfframes = 0
	renderframes = 0

	space = pymunk.Space()
	collisionBallBall = space.add_collision_handler(collisionTypes["ball"], collisionTypes["ball"])
	collisionBallBall.post_solve = switch_ball

	#space.gravity = (0.0, 900.0)
	space.iterations = 1
	#space.use_spatial_hash(5,40000)

	lines = add_environment(space)
	blueballs = []
	redballs = []
	greenballs = []
	ticks_to_next_blueball = 2
	ticks_to_next_redball = 2
	ticks_to_next_greenball = 2

	screen.fill((0,0,0))
	draw_lines(screen, lines)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sys.exit(0)
			elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				sys.exit(0)
		
		ticks_to_next_blueball -= 1
		if ticks_to_next_blueball <= 0:
			ticks_to_next_blueball = 2
			ball_shape, ball_body = add_ball(space, screenwidth/3, screenheight/2)
			ball_body.apply_impulse_at_local_point((random.randint(-15, 15),random.randint(-15, 15)))
			blueballs.append(ball_shape)
		
		ticks_to_next_redball -= 1
		if ticks_to_next_redball <= 0:
			ticks_to_next_redball = 2
			ball_shape, ball_body = add_ball(space, (screenwidth/3)*2, screenheight/2)
			ball_body.apply_impulse_at_local_point((random.randint(-15, 15),random.randint(-15, 15)))
			redballs.append(ball_shape)
		
		ticks_to_next_greenball -= 1
		if ticks_to_next_greenball <= 0:
			ticks_to_next_greenball = 4
			ball_shape, ball_body = add_ball(space, 390, 140)
			ball_body.apply_impulse_at_local_point((random.randint(-15, 15),random.randint(-15, 15)))
			greenballs.append(ball_shape)

		space.step(1/framerate)

		#screen.fill((0,0,0))

		# t1 = threading.Thread(target=draw_balls, args=(screen, blueballs, (0, 0, 255)))
		# t2 = threading.Thread(target=draw_balls, args=(screen, redballs, (255, 0, 0)))
		# t3 = threading.Thread(target=draw_balls, args=(screen, greenballs, (0, 255, 0)))
		
		# t1.start()
		# t2.start()
		# t3.start()
		
		# t1.join()
		# t2.join()
		# t3.join()
		renderframes -= 1
		if renderframes <= 0:
			cellsurface = pygame.Surface(screensize)
			cellarray = np.zeros((int(screenwidth / cellsize), int(screenheight / cellsize), 4), dtype = np.int16) # Cellgrid X, Cellgrid Y, and RGB+Count 

			if len(blueballs) > 0: draw_balls_cells(cellarray, cellsize, blueballs, (0, 0, 255))
			if len(redballs) > 0: draw_balls_cells(cellarray, cellsize, redballs, (255, 0, 0))
			if len(greenballs) > 0: draw_balls_cells(cellarray, cellsize, greenballs, (0, 255, 0))

			draw_cell_array(cellsurface, cellarray)
			draw_lines(cellsurface, lines)
			cellsurface.set_alpha(int(255/(framerate)))
			renderframes = framerate
		if renderframes % 2 == 0:
			#pixelarray = np.empty(screen.get_size())

			screen.blit(cellsurface, (0,0))

			#if len(blueballs) > 0: draw_balls(screen, blueballs, (0, 0, 255))
			#if len(redballs) > 0: draw_balls(screen, redballs, (255, 0, 0))
			#if len(greenballs) > 0: draw_balls(screen, greenballs, (0, 255, 0))
			
			#pygame.surfarray.blit_array(screen, pixelarray)

			pygame.display.flip()
			

		perfframes += 1
		if perfframes == framerate:
			perfframes = 0
			perfnew = time.perf_counter()
			perfframetime = (perfnew - perfstart)/framerate
			print(f"{1/perfframetime} FPS, {len(blueballs)+len(redballs)+len(greenballs)} balls, {perfframetime/(len(blueballs)+len(redballs)+len(greenballs))} per ball")
			perfstart = perfnew
		clock.tick(framerate)

if __name__ == '__main__':
	sys.exit(main())



