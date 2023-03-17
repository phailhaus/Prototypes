import sys
import math
import pygame
import pygame.gfxdraw
from pygame.locals import *
import pymunk
import pymunk.pygame_util

from localgrids import Localgrid
from localgrids import genWalls
from localgrids import drawShape
import cameraTransform

pygame.init()

clock = pygame.time.Clock()

screenwidth = 800
screenheight = 600
screensize = (screenwidth, screenheight)

framerate = 60

def main():
	screen = pygame.display.set_mode(screensize)
	camera = cameraTransform.Camera()

	smoothingFactor = .33

	mainspace = pymunk.Space()
	mainspace.gravity = (0.0, 500)

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

	# playerbody = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
	# playerbody.position = pymunk.Vec2d(screenwidth * .1, screenheight * .1)
	# playerbox = pymunk.Poly.create_box(playerbody, (25, 50), radius=2)
	# playerbox.elasticity = .1
	# playerbox.friction = 1
	# playerbox.density = 1

	# mainspace.add(playerbody, playerbox)

	player = CharacterController(mainspace, (80, 80))

	while True:
		for event in pygame.event.get():
					if event.type == QUIT:
						sys.exit(0)
					elif event.type == KEYDOWN:
						if event.key == K_ESCAPE: sys.exit(0)
						elif event.key == K_w: player.jumping = True

		keyspressed = pygame.key.get_pressed()
		if keyspressed[K_UP] or keyspressed[K_KP8]: camera.move(y = -5) # Up
		if keyspressed[K_DOWN] or keyspressed[K_KP5]: camera.move(y = 5) # Down
		if keyspressed[K_LEFT] or keyspressed[K_KP4]: camera.move(x = -5) # Left
		if keyspressed[K_RIGHT] or keyspressed[K_KP6]: camera.move(x = 5) # Right
		#if keyspressed[K_KP7]: camera.rotate(-60/framerate) # Rotate counter-clockwise
		#if keyspressed[K_KP9]: camera.rotate(60/framerate) # Rotate clockwise
		if keyspressed[K_KP_PLUS]: camera.zoom(.2/framerate) # Zoom in
		if keyspressed[K_KP_MINUS]: camera.zoom(-.2/framerate) # Zoom out
        
		if keyspressed[K_a]: player.moving_left = True
		if keyspressed[K_d]: player.moving_right = True
        
		player.update()
		mainspace.step(1/framerate)
		camera.smooth(posTarget = (player.body.position.x, player.body.position.y), smoothingFactor = smoothingFactor)

		screen.fill((0, 0, 0))

		movingenvironmentverts = list()
		for vert in environmentverts:
			movingenvironmentverts.append(camera.transformCoord(screen, vert))
		pygame.gfxdraw.aapolygon(screen, movingenvironmentverts, (255, 255, 255)) # Draw Walls
		drawShape(screen, objectbox, (255, 255, 255), pymunk.Vec2d(0,0), 0, camera) # Draw parent box
		drawShape(screen, player.shape, (255, 255, 255), pymunk.Vec2d(0,0), 0, camera) # Draw player box

		# pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(100, 100, screenwidth - 200, screenheight - 200), 2)
		
		# squigglepoints = list()
		# for i in range(6):
		# 	y = (i * 50) + 50
		# 	for x in (50, 200):
		# 		squigglepoints.append(camera.transformCoord(screen, (x, y)))
			
		# pygame.draw.aalines(screen, (255,255,255), False, squigglepoints)

		pygame.display.flip()

		clock.tick(framerate)
		#print(clock.get_fps())

class CharacterController:
    def __init__(self, space, pos=(0,0), radius=50, density=1.0):
        # create the character's physics body and shape
        self.body = pymunk.Body(body_type = pymunk.Body.DYNAMIC)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.friction = 1
        self.shape.elasticity = 0.0
        self.shape.density = density
        self.shape.collision_type = 1  # set collision type to 1 for character

        # add the body and shape to the space
        space.add(self.body, self.shape)

        # initialize movement variables
        self.moving_left = False
        self.moving_right = False
        self.jumping = False

    def update(self):
        # apply gravity to the character
        #self.body.apply_force_at_local_point(GRAVITY, (0, 0))

        # handle left/right movement
        if self.moving_left:
            self.shape.surface_velocity = (300, 300)
            self.moving_left = False
        elif self.moving_right:
            self.shape.surface_velocity = (-300, -300)
            self.moving_right = False
        else:
            self.shape.surface_velocity = (0, 0)

        # handle jumping
        if self.jumping:# and self.on_ground():
            self.body.apply_impulse_at_local_point(pymunk.Vec2d(0, -10000000).rotated(-self.body.angle), (0, 0))
            self.jumping = False

    def on_ground(self):
        # check if the character is in contact with a surface below it
        query_point = self.body.position + (0, -self.shape.radius - 1)  # point slightly below character center
        info = self.shape.space.point_query(query_point)
        for hit in info:
            if hit.shape.collision_type != self.shape.collision_type:
                normal = hit.normal
                if normal.y > 0.5:  # check if normal is pointing mostly upwards
                    return True
        return False

if __name__ == '__main__':
	sys.exit(main())

