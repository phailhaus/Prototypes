import math
import random

import pygame
from pygame.math import Vector2
from pygame.locals import *
import pygame.freetype
import pygame.gfxdraw

# Initialize Pygame
pygame.init()

# Load default font
defaultFont = pygame.freetype.Font(None, 12)

# Set the dimensions of the screen
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Set Map display size
map_render_width, map_render_height = 600, 300

# Set render distance in world units
render_distance = 600
render_distance_squared = render_distance ** 2

# Set Camera
camera_fov = 40
camera_fov_radians = (camera_fov * math.pi) / 180
camera_vfov_radians = 2 * math.atan(math.tan(camera_fov_radians / 2) * (screen_width/screen_height))
camera_distance = 10 # Camera distance behind the screen
screen_width_world_coords = 2 * camera_distance * math.sin(camera_fov_radians/2)

# Set default wall height
wall_height = 100

# Set % of screen height to drop per unit of distance
perspective_drop_ratio = .001 # % of screen height to drop per unit of distance
perspective_unit_shift = 30 # Shift wall scaling by this many units to allow walls to be taller than the screen when close to them

# Set up the clock object
clock = pygame.time.Clock()
framerate = 30

# Set the title of the window
pygame.display.set_caption("Wolf3D!")

# Player Controller
class Player:
	def __init__(self):
		self.position = Vector2((0, 0))
		self.angle = Vector2((1, 0))
		self.width = 10
		self.camera_width = self.width - 8
		self.camera_fov = camera_fov
	
	def move(self, distance, normal = False):
		movementvector = self.angle.rotate(-90 * normal)
		movementvector.scale_to_length(distance)
		self.position = self.position + movementvector
	
	def rotate(self, rotation):
		self.angle.rotate_ip(rotation)
	
	def render(self, surface, environment, debugsurface = None):
		render_width, render_height = surface.get_width(), surface.get_height()
		if debugsurface != None:
			localdebugsurface = pygame.Surface(debugsurface.get_size(), flags = pygame.SRCALPHA)
		
		for screen_x in range(render_width):
			collisions = list()
			
			render_progress = screen_x / (render_width - 1)
			
			#camera_offset = self.camera_width * (render_progress - .5) # Creates base of frustum. First col is offset -self.camera_width / 2, last col + self.camera_width / 2
			#offset_vector = self.angle.rotate(90) # Rotate player angle vector to the side, returning a copy
			#offset_vector.scale_to_length(camera_offset) # Scale the vector to the number of units it needs to be offset
			#camera_position = self.position + offset_vector # Offset camera position from player position
			
			#ray_angle = self.camera_fov * (render_progress - .5)
			#correction_factor = 1 # (((1/math.cos(math.radians(ray_angle))) - 1) * -5) + 1
			#camera_angle = self.angle.rotate(ray_angle) # Rotate player angle slightly based on render progress to make taper of frustum
			#camera_angle.scale_to_length(render_distance) # Scale to length of ray

			camera_offset = Vector2(self.angle)
			camera_offset.scale_to_length(camera_distance)
			camera_position = self.position - camera_offset
			screen_offset = Vector2(self.angle).rotate(-90)
			screen_offset.scale_to_length(screen_width_world_coords * -(render_progress - .5))
			pixel_position = self.position + screen_offset
			ray_vector = pixel_position - camera_position
			ray_vector.scale_to_length(render_distance)

			end_of_ray = pixel_position + ray_vector

			if debugsurface != None:
				pygame.draw.line(localdebugsurface, (255, 255, 255, abs(int(render_progress * 255)-127)), pixel_position, pixel_position + ray_vector)

			
			for wall in environment.walls:
				x1, y1 = pixel_position.xy
				x2, y2 = end_of_ray.xy
				x3, y3 = wall.start_point
				x4, y4 = wall.end_point

				# Following is taken from http://www.jeffreythompson.org/collision-detection/line-line.php
				if (y4-y3)*(x2-x1) != (x4-x3)*(y2-y1):
					uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
					uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
					if 0 <= uA <= 1 and 0 <= uB <= 1:
						intersectionX = x1 + (uA * (x2-x1))
						intersectionY = y1 + (uA * (y2-y1))
						distance_squared = ((uA * (x2-x1)) ** 2) + ((uA * (y2-y1)) ** 2)
						collisions.append((distance_squared, wall, (intersectionX, intersectionY)))
			
			len_collisions = len(collisions)
			if len_collisions:
				if len_collisions > 1:
					collisions.sort(key = lambda e : e[0])
				
				i = 0
				found_solid = False
				while found_solid == False and i < len_collisions: # Crawl down through the collision list until you find a solid wall
					if collisions[i][1].color.a != 255:
						i += 1
					else:
						found_solid = True
				
				while i >= 0: # Climb back up the collision list drawing the visible walls from furthest to nearest
					distance_squared, drawn_wall, wall_position = collisions[i]
					""" wall_position = Vector2(wall_position)
					if screen_x == int(render_width / 2): print(f"Starting wall coord: {wall_position}")
					wall_position = wall_position - self.position # Offset so that player/camera is at zero
					if screen_x == int(render_width / 2): print(f"Wall coord after offset: {wall_position}")
					wall_position.rotate_ip(self.angle.rotate(90).as_polar()[1]) # Rotate so that it is aligned with player/camera
					if screen_x == int(render_width / 2): print(f"Wall coord after rotate: {wall_position}")
					distance = abs(wall_position.y) """
					distance = math.sqrt(distance_squared)
					# lineshrink = (distance - perspective_unit_shift) * perspective_drop_ratio * render_height
					relative_height_radians = math.atan(wall_height/distance)
					line_length = min(max(render_height * (relative_height_radians/camera_vfov_radians), 1), render_height)
					line_offset = (render_height - line_length) / 2

					pygame.gfxdraw.vline(surface, screen_x, 0, int(line_offset), drawn_wall.rooms[0].ceiling_color) # Draw Ceiling

					if drawn_wall.color.a != 0: # Skip wall drawing if the wall is fully transparent
						draw_color = drawn_wall.color.lerp((30, 30, 30), distance_squared / render_distance_squared) # Provide distance-based darkening to make surfaces easier to understand
						if drawn_wall.color.a == 255:
							pygame.gfxdraw.vline(surface, screen_x, int(line_offset), int(line_offset + line_length), draw_color) # Draw Wall the easy way if it is fully opaque
						else:
							draw_color.a = drawn_wall.color.a # Make a surface the size/shape of the line, fill it, then blit it over the screen
							tempsurface = pygame.Surface((1, line_length))
							tempsurface.fill(draw_color)
							tempsurface.set_alpha(draw_color.a)
							surface.blit(tempsurface, (screen_x, line_offset), special_flags = BLEND_ALPHA_SDL2)
					
					pygame.gfxdraw.vline(surface, screen_x, int(line_offset + line_length), int(render_height), drawn_wall.rooms[0].floor_color) # Draw Floor

					i -= 1

		if debugsurface != None:
			debugsurface.blit(localdebugsurface, (0,0))

class Wall:
	def __init__(self, room, color):
		self.start_point = None
		self.end_point = None
		self.color = pygame.Color(color)
		self.rooms = list()
		self.rooms.append(room)
		self.rooms[0].environment.walls.append(self)
	
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
		wall.rooms.append(self)
	
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
		self.walls = list()
	
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
environment.rooms[0].add_wall_abs((159, 194), (255, 127, 39, 0))
environment.rooms[0].add_wall_abs((41, 194), (255, 242, 0))
environment.rooms[0].add_wall_abs((5, 76), (34, 177, 76))
environment.rooms[0].add_wall_abs((100, 4), (0, 162, 232))

environment.add_room(floor_color=(25, 60, 25), ceiling_color=(127, 180, 127))
environment.rooms[1].add_wall_existing(environment.rooms[0].walls[1])
environment.rooms[1].add_wall_abs((425, 194), (255, 201, 14))
environment.rooms[1].add_wall_abs((425, 77), (239, 228, 176, 127))
environment.rooms[1].add_wall_abs((196, 76), (181, 230, 29))

environment.add_room(floor_color=(60, 25, 25), ceiling_color=(180, 127, 127))
environment.rooms[1].add_wall_existing(environment.rooms[1].walls[2])
environment.rooms[1].add_wall_abs((425, 10), (163, 73, 164))
environment.rooms[1].add_wall_abs((471, 57), (255, 242, 0))
environment.rooms[1].add_wall_abs((512, 21), (34, 177, 76))
environment.rooms[1].add_wall_abs((564, 98), (0, 162, 232))
environment.rooms[1].add_wall_abs((588, 289), (153, 217, 234))
environment.rooms[1].add_wall_abs((425, 277), (112, 146, 190))
environment.rooms[1].add_wall_abs((425, 194), (200, 191, 231))

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
		if event.type == pygame.KEYDOWN:
			if event.key == K_c: # Hide the mouse
				pygame.mouse.set_visible(not pygame.mouse.get_visible())
				pygame.event.set_grab(not pygame.event.get_grab())
			elif event.key == K_KP_9: # Debug FOV up
				player.camera_fov += 10
				print(player.camera_fov)
			elif event.key == K_KP_6: # Debug FOV down
				player.camera_fov -= 10
				print(player.camera_fov)
			elif event.key == K_KP_8: # Debug camera width up
				player.camera_width += 1
				print(player.camera_width)
			elif event.key == K_KP_5: # Debug camera width down
				player.camera_width -= 1
				print(player.camera_width)
	
	mousemovement = pygame.mouse.get_rel() # Get mouse movement in this frame
	player.rotate(mousemovement[0] * .15)


	keyspressed = pygame.key.get_pressed()
	if keyspressed[K_a]: player.move(3, True) # Left
	if keyspressed[K_d]: player.move(-3, True) # Right
	if keyspressed[K_w]: player.move(3) # Forward
	if keyspressed[K_s]: player.move(-3) # Back
	if keyspressed[K_q]: player.rotate(-3) # Rotate counter-clockwise
	if keyspressed[K_e]: player.rotate(3) # Rotate clockwise

	# Top-down display
	mapsurface = pygame.Surface((map_render_width, map_render_height), flags=pygame.SRCALPHA)
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