import sys
import math
import pygame
import pygame.gfxdraw
from pygame.locals import *
import pymunk
import pymunk.pygame_util

pygame.init()

clock = pygame.time.Clock()

screenwidth = 800
screenheight = 600
screensize = (screenwidth, screenheight)

framerate = 60

def main():
	debugdraw = False

	screen = pygame.display.set_mode(screensize)
	mainspace = pymunk.Space()
	mainspace.gravity = (0.0, 100)

	environmentbody = pymunk.Body(body_type = pymunk.Body.STATIC)
	environmentverts, environmentsegments = genWalls(environmentbody, screenwidth, screenheight)
	mainspace.add(environmentbody)
	for segment in environmentsegments:
		mainspace.add(segment)

	objectbody = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
	objectbody.position = pymunk.Vec2d(screenwidth * .5, screenheight * .5)
	objectbody.angular_velocity = .5
	objectbody.velocity = pymunk.Vec2d(40, 100)
	objectbox = pymunk.Poly.create_box(objectbody, (screenwidth * .25, screenheight * .25), radius=5)
	objectbox.elasticity = .1
	objectbox.density = 1

	mainspace.add(objectbody, objectbox)

	objectspace = pymunk.Space()
	objectspace.gravity = (0.0, 0.0)
	objectenvironmentbody = pymunk.Body(body_type = pymunk.Body.STATIC)
	objectenvironmentverts, objectenvironmentsegments = genWalls(objectenvironmentbody, screenwidth * .25, screenheight * .25)
	objectspace.add(objectenvironmentbody)
	for segment in objectenvironmentsegments:
		objectspace.add(segment)
	
	innerobjectbody = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
	innerobjectbody.position = pymunk.Vec2d(screenwidth * .125, screenheight * .125)
	innerobjectbody.angular_velocity = .5
	innerobjectbody.velocity = pymunk.Vec2d(10, 25)
	innerobjectbox = pymunk.Poly.create_box(innerobjectbody, (screenwidth * .25 * .25, screenheight * .25 * .25), radius=5)
	innerobjectbox.elasticity = .1
	innerobjectbox.density = 1

	objectspace.add(innerobjectbody, innerobjectbox)

	while True:
		for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit(0)
					elif event.type == KEYDOWN:
						if event.key == K_ESCAPE:
							sys.exit(0)
						elif event.key == K_d:
							debugdraw = not debugdraw

		innerobjectbody.prestepvelocity = objectbody.velocity_at_local_point(innerobjectbody.position)
		innerobjectbody.prestepangvelocity = objectbody.angular_velocity

		keyspressed = pygame.key.get_pressed()
		if keyspressed[K_UP] or keyspressed[K_KP8]: fire_engine(objectbody, (0,-1))
		if keyspressed[K_DOWN] or keyspressed[K_KP5]: fire_engine(objectbody, (0,1))
		if keyspressed[K_KP7]: fire_engine(objectbody, (-1, 0))
		if keyspressed[K_KP9]: fire_engine(objectbody, (1, 0))
		if keyspressed[K_LEFT] or keyspressed[K_KP4]: objectbody.angular_velocity -= .01
		if keyspressed[K_RIGHT] or keyspressed[K_KP6]: objectbody.angular_velocity += .01
		
		mainspace.step(1/framerate)

		innerobjectbody.poststepvelocity = objectbody.velocity_at_local_point(innerobjectbody.position)
		innerobjectbody.poststepangvelocity = objectbody.angular_velocity
		
		acceleration = (innerobjectbody.poststepvelocity - innerobjectbody. prestepvelocity).rotated(-objectbody.angle + math.radians(180))
		velocityadd = acceleration + (mainspace.gravity.rotated(-objectbody.angle)/framerate)
		innerobjectbody.velocity += velocityadd

		angularacceleration = innerobjectbody.poststepangvelocity - innerobjectbody.prestepangvelocity
		innerobjectbody.angular_velocity -= angularacceleration


		objectspace.step(1/framerate)
		screen.fill((0, 0, 0))
		pygame.gfxdraw.aapolygon(screen, environmentverts, (255, 255, 255)) # Draw Walls
		drawPoly(screen, objectbox, (255, 255, 255), pymunk.Vec2d(0,0), 0)
		drawPoly(screen, innerobjectbox, (255, 255, 255), objectbox.body.local_to_world(objectbox.get_vertices()[3]), objectbox.body.angle)

		if debugdraw:
			debugpos = innerobjectbox.body.position.rotated(objectbox.body.angle) + objectbox.body.local_to_world(objectbox.get_vertices()[3])
			debugposx, debugposy = debugpos
			debugaccelposx, debugaccelposy = debugpos + acceleration.rotated(objectbox.body.angle) * 10
			debugveladdposx, debugveladdposy = debugpos + velocityadd.rotated(objectbox.body.angle) * 10
			pygame.draw.aaline(screen, (255, 0, 0), (debugposx, debugposy), (debugaccelposx, debugaccelposy))
			pygame.draw.aaline(screen, (0, 255, 0), (debugposx, debugposy), (debugveladdposx, debugveladdposy))

		pygame.display.flip()

		clock.tick(framerate)
		print(clock.get_fps())

def fire_engine(objectbody, direction=(0,-1), force=None):
		if force==None:
			force = 20000/framerate
		direction = pymunk.Vec2d(direction[0], direction[1]).normalized()
		if direction == 0:
			return
		objectbody.apply_force_at_local_point((force * direction.x * objectbody.mass, force * direction.y * objectbody.mass))

def drawPoly(screen=pygame.display, poly = pymunk.Poly, color = tuple, position = pymunk.vec2d, angle = float):
	verts = list()
	for v in poly.get_vertices():
		v = v.rotated(poly.body.angle) + poly.body.position
		x,y = v.rotated(angle) + position
		verts.append((x, y))
	pygame.gfxdraw.aapolygon(screen, verts, color)

def genWalls(body, width, height):
	verts = list()
	segs = list()
	verts.append((0, 0))
	verts.append((width-1, 0))
	verts.append((width-1, height-1))
	verts.append((0, height-1))
	for i in range(4):
		if i < 3:
			firstvert = verts[i]
			secondvert = verts[i+1]
		else:
			firstvert = verts[i]
			secondvert = verts[0]
		segs.append(pymunk.Segment(body, firstvert, secondvert, radius = 0))
		segs[-1].elasticity = .99
	return verts, segs
			




if __name__ == '__main__':
	sys.exit(main())