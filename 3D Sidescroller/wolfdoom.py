import math
import random

import pygame
from pygame.math import Vector2
from pygame.locals import *
import pygame.freetype

# Initialize Pygame
pygame.init()

# Load default font
defaultFont = pygame.freetype.Font(None, 12)

# Set the dimensions of the screen
screen_width = 1600
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Set Map display size
map_render_width, map_render_height = 300, 300

# Set render distance in world units
render_distance = 300
render_distance_squared = render_distance ** 2

# Set up the clock object
clock = pygame.time.Clock()
framerate = 30

# Set the title of the window
pygame.display.set_caption("3D!")

# Player Controller
class Player:
	def __init__(self):
		self.position = Vector2((0, 0))
		self.angle = Vector2((1, 0))
		self.width = 10
		self.camera_width = self.width - 2
		self.camera_fov = 60
	
	def move(self, distance, normal = False):
		movementvector = self.angle.rotate(-90 * normal)
		movementvector.scale_to_length(distance)
		self.position = self.position + movementvector
	
	def rotate(self, rotation):
		self.angle.rotate_ip(rotation)
	
	def render(self, surface, environment, debugsurface = None):
		render_size = surface.get_size()
		render_width, render_height = render_size[0], render_size[1]
		for screen_x in range(render_width):
			collisions = list()
			
			render_progress = screen_x / (render_width - 1)
			
			camera_offset = self.camera_width * (render_progress - .5) # Creates base of frustum. First col is offset -self.camera_width / 2, last col + self.camera_width / 2
			offset_vector = self.angle.rotate(90) # Rotate player angle vector to the side, returning a copy
			offset_vector.scale_to_length(camera_offset) # Scale the vector to the number of units it needs to be offset
			camera_position = self.position + offset_vector # Offset camera position from player position
			
			camera_angle = self.angle.rotate(self.camera_fov * (render_progress - .5)) # Rotate player angle slightly based on render progress to make taper of frustum
			camera_angle.scale_to_length(render_distance) # Scale to length of ray

			end_of_ray = camera_position + camera_angle

			if debugsurface != None:
				if render_progress == 0 or render_progress == 1:
					pygame.draw.line(debugsurface, (255, 255, 255, int(render_progress * 255)), camera_position, camera_position + camera_angle)

			for room in environment.rooms:
				for wall in room.walls:
					x1, y1 = camera_position.xy
					x2, y2 = end_of_ray.xy
					x3, y3 = wall.start_point
					x4, y4 = wall.end_point

					# Following is taken from http://www.jeffreythompson.org/collision-detection/line-line.php
					if (y4-y3)*(x2-x1) != (x4-x3)*(y2-y1):
						uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
						uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
						if 0 <= uA <= 1 and 0 <= uB <= 1:
							# intersectionX = x1 + (uA * (x2-x1))
							# intersectionY = y1 + (uA * (y2-y1))
							distancesqrd = ((uA * (x2-x1)) ** 2) + ((uA * (y2-y1)) ** 2)
							collisions.append((distancesqrd, wall))
			
			if len(collisions) > 0:
				if len(collisions) > 1:
					collisions.sort()
				distance_squared, drawn_wall = collisions[0]
				line_length = render_height * (1 - (distance_squared / render_distance_squared))
				line_offset = (render_height - line_length) / 2
				pygame.draw.line(surface, drawn_wall.rooms[0].ceiling_color, (screen_x, 0), (screen_x, line_offset))	# Draw Ceiling		
				pygame.draw.line(surface, drawn_wall.color, (screen_x, line_offset), (screen_x, line_offset + line_length))	# Draw Wall		
				pygame.draw.line(surface, drawn_wall.rooms[0].floor_color, (screen_x, line_offset + line_length), (screen_x, render_height))	# Draw Floor		

class Wall:
	def __init__(self, room, color):
		self.start_point = None
		self.end_point = None
		self.color = color
		self.rooms = list()
		self.rooms.append(room)
	
	def place_abs(self, start_point, end_point):
		self.start_point = start_point
		self.end_point = end_point
	
	def draw_to_map(self, surface):
		pygame.draw.aaline(surface, self.color, self.start_point, self.end_point)

class Room:
	def __init__(self, environment, floor_color, ceiling_color):
		self.environment = environment
		self.floor_color = floor_color
		self.ceiling_color = ceiling_color
		self.walls = list()
	
	def add_wall_existing(self, wall):
		self.walls.append(wall)
	
	def add_wall_first(self, start_point, end_point, color):
		self.walls.append(Wall(self, color))
		self.walls[-1].place_abs(start_point, end_point)
	
	def add_wall_abs(self, end_point, color):
		self.walls.append(Wall(self, color))
		self.walls[-1].place_abs(self.walls[-2].end_point, end_point)
	
	def draw_to_map(self, surface):
		for wall in self.walls:
			wall.draw_to_map(surface)

class Environment:
	def __init__(self):
		self.rooms = list()
	
	def add_room(self, floor_color = (0, 0, 0), ceiling_color = (0, 0, 0)):
		self.rooms.append(Room(self, floor_color, ceiling_color))
	
	def draw_to_map(self, surface):
		for room in self.rooms:
			room.draw_to_map(surface)

player = Player()
player.position = Vector2((50, 50))

environment = Environment()
environment.add_room(floor_color=(25, 25, 25), ceiling_color=(127, 127, 127))
environment.rooms[0].add_wall_first((100, 4), (196, 76), (237, 28, 36))
environment.rooms[0].add_wall_abs((159, 194), (255, 127, 39))
environment.rooms[0].add_wall_abs((41, 194), (255, 242, 0))
environment.rooms[0].add_wall_abs((5, 76), (34, 177, 76))
environment.rooms[0].add_wall_abs((100, 4), (0, 162, 232))

# Game loop
running = True
frame = 0
while running:
	# Limit the framerate
	clock.tick(framerate)

	# Handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			running = False
		if event.type == pygame.KEYDOWN and event.key == K_c: # Hide the mouse
			pygame.mouse.set_visible(not pygame.mouse.get_visible())
			pygame.event.set_grab(not pygame.event.get_grab())
	
	mousemovement = pygame.mouse.get_rel() # Get mouse movement in this frame
	player.rotate(mousemovement[0] * .15)


	keyspressed = pygame.key.get_pressed()
	if keyspressed[K_a]: player.move(1, True) # Left
	if keyspressed[K_d]: player.move(-1, True) # Right
	if keyspressed[K_w]: player.move(1) # Forward
	if keyspressed[K_s]: player.move(-1) # Back
	if keyspressed[K_q]: player.rotate(-3) # Rotate counter-clockwise
	if keyspressed[K_e]: player.rotate(3) # Rotate clockwise

	# Top-down display
	mapsurface = pygame.Surface((map_render_width, map_render_height))
	environment.draw_to_map(mapsurface)
	scaledposition = player.position * 8 # Scale from 100x100 space to screen size
	lineoffset = Vector2(player.angle)
	lineoffset.scale_to_length(100)
	lineredpoint = player.position + lineoffset
	pygame.draw.aaline(mapsurface, (255, 0, 0), player.position, lineredpoint)

	# 3D Display
	gamesurface = pygame.Surface((screen_width, screen_height))
	player.render(gamesurface, environment, mapsurface)


	# Draw surfaces
	screen.fill((0, 0, 0)) # Clear the screen
	screen.blit(gamesurface, (0, 0))
	screen.blit(mapsurface, (0, 0))

	# Update the screen
	pygame.display.flip()
	frame += 1

# Clean up
pygame.quit()