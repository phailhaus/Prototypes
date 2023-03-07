import sys
import math
import pygame
import pygame.gfxdraw
from pygame.locals import *
import pymunk
import pymunk.pygame_util

import cameraTransform

pygame.init()

clock = pygame.time.Clock()

screenwidth = 800
screenheight = 600
screensize = (screenwidth, screenheight)

framerate = 60

class Localgrid:
	def __init__(self, parentbody, defaultcolor = (255, 255, 255)):
		self.parentbody = parentbody
		self.defaultcolor = defaultcolor
		self.space = pymunk.Space()
		self.bodies = list()
		self.shapes = list()		
	
	def addBodies(self, *bodies):
		for body in bodies:
			self.bodies.append(body)
			self.space.add(body)
	
	def addShapes(self, *shapes):
		for shape in shapes:
			try: shape.hidden
			except AttributeError: shape.hidden = False

			try: shape.color
			except AttributeError: shape.color = self.defaultcolor

			self.shapes.append(shape)
			self.space.add(shape)

		
	
	def prestep(self):
		for body in self.bodies:
			if body.body_type == pymunk.Body.DYNAMIC:
				body.prestepvelocity = self.parentbody.velocity_at_local_point(body.position) # Record absolute velocity of the parent object at the location of the child object
				body.prestepangvelocity = self.parentbody.angular_velocity # Record angular velocity of the parent object
	
	def poststep(self):
		for body in self.bodies:
			if body.body_type == pymunk.Body.DYNAMIC:
				body.poststepvelocity = self.parentbody.velocity_at_local_point(body.position) # Record absolute velocity again after the timestep so that acceleration can be computed
				body.poststepangvelocity = self.parentbody.angular_velocity # Record angular velocity again so that angular acceleration can be computed

				body.acceleration = (body.poststepvelocity - body.prestepvelocity).rotated(-self.parentbody.angle + math.radians(180)) # Calculate acceleration of the parent, rotate it by parent angle to translate it into child space, and flip it so that the child gets the opposite acceleration
				body.velocityadd = body.acceleration + (self.parentbody.space.gravity.rotated(-self.parentbody.angle)/framerate) # Add gravity to the acceleration. If parent is in freefall, gravity on the parent and this gravity will cancel out, providing weightlessness.
				body.velocity += body.velocityadd # Apply acceleration/gravity to child

				angularacceleration = body.poststepangvelocity - body.prestepangvelocity # Calculate angular acceleration of the parent
				body.angular_velocity -= angularacceleration # Subtract angular acceleration from the child

	def step(self, dt):
		self.space.step(dt)
	
	def draw(self, screen, camera = None):
		for shape in self.shapes:
			if not shape.hidden:
				if camera == None:
					drawShape(screen, shape, shape.color, self.parentbody.position, self.parentbody.angle)
				else:
					drawShape(screen, shape, shape.color, self.parentbody.position, self.parentbody.angle, camera = camera)
	
	def debugdraw(self, screen, camera = None):
		for body in self.bodies:
			if body.body_type == pymunk.Body.DYNAMIC:
				debugpos = body.position.rotated(self.parentbody.angle) + self.parentbody.position
				debugposx, debugposy = debugpos
				debugaccelposx, debugaccelposy = debugpos + body.acceleration.rotated(self.parentbody.angle) * 10
				debugveladdposx, debugveladdposy = debugpos + body.velocityadd.rotated(self.parentbody.angle) * 10
				if camera == None:
					pygame.draw.aaline(screen, (255, 0, 0), (debugposx, debugposy), (debugaccelposx, debugaccelposy))
					pygame.draw.aaline(screen, (0, 255, 0), (debugposx, debugposy), (debugveladdposx, debugveladdposy))
				else:
					pygame.draw.aaline(screen, (255, 0, 0), camera.transformCoord(screen, (debugposx, debugposy)), camera.transformCoord(screen, (debugaccelposx, debugaccelposy)))
					pygame.draw.aaline(screen, (0, 255, 0), camera.transformCoord(screen, (debugposx, debugposy)), camera.transformCoord(screen, (debugveladdposx, debugveladdposy)))
				

def main():
	debugdraw = False
	movingcamera = False
	smoothingFactor = .33
	camera = cameraTransform.Camera(position = (screenwidth / 2, screenheight / 2))

	screen = pygame.display.set_mode(screensize)
	mainspace = pymunk.Space()
	mainspace.gravity = (0.0, 100)

	environmentbody = pymunk.Body(body_type = pymunk.Body.STATIC)
	environmentverts, environmentsegments = genWalls(environmentbody, screenwidth, screenheight)
	mainspace.add(environmentbody)
	for segment in environmentsegments:
		segment.friction = 1
		mainspace.add(segment)

	objectbody = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
	objectbody.position = pymunk.Vec2d(screenwidth * .5, screenheight * .5)
	objectbody.angular_velocity = .5
	objectbody.velocity = pymunk.Vec2d(40, 100)
	objectbox = pymunk.Poly.create_box(objectbody, (screenwidth * .25, screenheight * .25), radius=5)
	objectbox.elasticity = .1
	objectbox.friction = 1
	objectbox.density = 1

	mainspace.add(objectbody, objectbox)

	objectbody.localgrid = Localgrid(objectbody)

	localgridenvironmentbody = pymunk.Body(body_type = pymunk.Body.STATIC)
	localgridenvironmentverts, localgridenvironmentsegments = genWalls(localgridenvironmentbody, screenwidth * .25, screenheight * .25, centered=True)
	objectbody.localgrid.addBodies(localgridenvironmentbody)
	for segment in localgridenvironmentsegments:
		segment.friction = 1
		segment.hidden = True
		objectbody.localgrid.addShapes(segment)
	
	innerobjectbody = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
	innerobjectbody.position = pymunk.Vec2d(0, 0)
	innerobjectbody.angular_velocity = .5
	innerobjectbody.velocity = pymunk.Vec2d(10, 25)
	innerobjectbox = pymunk.Poly.create_box(innerobjectbody, (screenwidth * .25 * .25, screenheight * .25 * .25), radius=5)
	innerobjectbox.elasticity = .1
	innerobjectbox.friction = 1
	innerobjectbox.density = 1

	objectbody.localgrid.addBodies(innerobjectbody)
	objectbody.localgrid.addShapes(innerobjectbox)

	for i in range(6):
		circlebody = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
		circle = pymunk.Circle(circlebody, screenwidth * .1 * .25)
		circle.elasticity = .1
		circle.friction = 1
		circle.density = 1
		objectbody.localgrid.addBodies(circlebody)
		objectbody.localgrid.addShapes(circle)

	while True:
		for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit(0)
					elif event.type == KEYDOWN:
						if event.key == K_ESCAPE:
							sys.exit(0)
						elif event.key == K_d: debugdraw = not debugdraw
						elif event.key == K_c: movingcamera = not movingcamera

		objectbody.localgrid.prestep()

		keyspressed = pygame.key.get_pressed()
		if keyspressed[K_UP] or keyspressed[K_KP8]: fire_engine(objectbody, (0,-1)) # Up
		if keyspressed[K_DOWN] or keyspressed[K_KP5]: fire_engine(objectbody, (0,1)) # Down
		if keyspressed[K_LEFT] or keyspressed[K_KP4]: fire_engine(objectbody, (-1, 0)) # Left
		if keyspressed[K_RIGHT] or keyspressed[K_KP6]: fire_engine(objectbody, (1, 0)) # Right
		if keyspressed[K_KP7]: objectbody.angular_velocity -= 1/framerate # Rotate counter-clockwise
		if keyspressed[K_KP9]: objectbody.angular_velocity += 1/framerate # Rotate clockwise
		if keyspressed[K_z]: # Increase smoothing
			smoothingFactor -= .1 / framerate
			if smoothingFactor < 0:
				smoothingFactor = 0
			print(smoothingFactor)
		if keyspressed[K_x]: # Reduce smoothing
			smoothingFactor += .1 / framerate
			if smoothingFactor > 1:
				smoothingFactor = 1
			print(smoothingFactor)

		
		mainspace.step(1/framerate)

		camera.smooth(posTarget = (objectbody.position.x, objectbody.position.y), rotTarget = -objectbody.angle/math.tau, smoothingFactor = smoothingFactor)

		objectbody.localgrid.poststep()

		objectbody.localgrid.step(1/framerate)

		screen.fill((0, 0, 0))
		if not movingcamera:
			pygame.gfxdraw.aapolygon(screen, environmentverts, (255, 255, 255)) # Draw Walls
			drawShape(screen, objectbox, (255, 255, 255), pymunk.Vec2d(0,0), 0) # Draw parent box
			objectbody.localgrid.draw(screen)

			if debugdraw:
				objectbody.localgrid.debugdraw(screen)

		elif movingcamera:
			movingenvironmentverts = list()
			for vert in environmentverts:
				movingenvironmentverts.append(camera.transformCoord(screen, vert))
			pygame.gfxdraw.aapolygon(screen, movingenvironmentverts, (255, 255, 255)) # Draw Walls
			drawShape(screen, objectbox, (255, 255, 255), pymunk.Vec2d(0,0), 0, camera) # Draw parent box
			objectbody.localgrid.draw(screen, camera = camera)

			if debugdraw:
				objectbody.localgrid.debugdraw(screen, camera = camera)

		pygame.display.flip()

		clock.tick(framerate)
		#print(clock.get_fps())

def fire_engine(objectbody, direction=(0,-1), force=None):
		if force==None:
			force = 20000/framerate
		direction = pymunk.Vec2d(direction[0], direction[1]).normalized()
		if direction == 0:
			return
		objectbody.apply_force_at_local_point((force * direction.x * objectbody.mass, force * direction.y * objectbody.mass))

def drawShape(screen, shape, color, position, angle, camera = None):
	if type(shape) == pymunk.shapes.Poly:
		verts = list()
		for v in shape.get_vertices():
			v = v.rotated(shape.body.angle) + shape.body.position
			x,y = v.rotated(angle) + position
			if camera == None:
				verts.append((x, y))
			else:
				verts.append(camera.transformCoord(screen, (x, y)))
		pygame.gfxdraw.aapolygon(screen, verts, color)
	elif type(shape) == pymunk.shapes.Circle:
		c = shape.offset.rotated(shape.body.angle) + shape.body.position
		c = c.rotated(angle) + position
		x, y = c
		if camera == None:
			pygame.gfxdraw.aacircle(screen, int(x), int(y), int(shape.radius), color)
		else:
			x, y = camera.transformCoord(screen, (x, y))
			pygame.gfxdraw.aacircle(screen, int(x), int(y), int(shape.radius * camera.scale), color)

def genWalls(body, width, height, centered = False):
	verts = list()
	segs = list()
	if not centered:
		verts.append((0, 0))
		verts.append((width-1, 0))
		verts.append((width-1, height-1))
		verts.append((0, height-1))
	elif centered:
		verts.append((-width/2, -height/2))
		verts.append((width/2, -height/2))
		verts.append((width/2, height/2))
		verts.append((-width/2, height/2))
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