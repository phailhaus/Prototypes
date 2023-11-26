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

# Set Default Camera
camera_vfov_degrees = 54
camera_distance = .5 # Camera distance behind the screen

# Set default wall height
wall_height = 3

# Set up the clock object
clock = pygame.time.Clock()
framerate = 30

# Set the title of the window
pygame.display.set_caption("Wolf3D!")

# Player Controller
class Player:
	def __init__(self):
		self.position = Vector2((0, 0))
		self.vertical_position = 0
		self.angle = Vector2((1, 0))
		self.width = 1
		self.height = 2
		self.movespeed_per_ms = .01
		self.camera_vfov_degrees = camera_vfov_degrees
		self.camera_distance = camera_distance
		self.update_fov()
	
	def update_fov(self, vfov = None, distance = None):
		if vfov != None:
			self.camera_vfov_degrees = vfov
		if distance != None:
			self.camera_distance = distance
		self.camera_vfov_radians = math.radians(self.camera_vfov_degrees)
		self.camera_hfov_radians = 2 * math.atan(math.tan(self.camera_vfov_radians / 2) * (screen_width/screen_height))
		self.camera_hfov_degrees = math.degrees(self.camera_hfov_radians)
		self.camera_aperture_width = 2 * self.camera_distance * math.sin(self.camera_hfov_radians/2)
	
	def print_camera_stats(self):
		print(f"VFOV: {self.camera_vfov_degrees}\nHFOV: {self.camera_hfov_degrees}\nDistance: {self.camera_distance}\nAperture Width: {self.camera_aperture_width}\n")
	
	def move(self, distance_scale, milliseconds, normal = False):
		movementvector = self.angle.rotate(-90 * normal)
		movementvector.scale_to_length(distance_scale * self.movespeed_per_ms * milliseconds)
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

			camera_offset = Vector2(self.angle)
			camera_offset.scale_to_length(self.camera_distance)
			camera_position = self.position - camera_offset
			screen_offset = Vector2(self.angle).rotate(-90)
			screen_offset.scale_to_length(self.camera_aperture_width * -(render_progress - .5))
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
					distance = math.sqrt(distance_squared)
					camera_height = self.vertical_position + self.height
					angle_bottom = math.atan((camera_height - drawn_wall.bottom_pos) / distance)
					angle_top = math.atan((drawn_wall.top_pos - camera_height) / distance)
					ratio_bottom = angle_bottom / (self.camera_vfov_radians / 2)
					ratio_top = angle_top / (self.camera_vfov_radians / 2)
					line_length = max((render_height / 2) * (ratio_bottom + ratio_top), 1)
					line_offset = (render_height / 2) * (1 - ratio_top)

					pygame.gfxdraw.vline(surface, screen_x, 0, int(line_offset), drawn_wall.room.ceiling_color) # Draw Ceiling

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
					
					pygame.gfxdraw.vline(surface, screen_x, int(line_offset + line_length), int(render_height), drawn_wall.room.floor_color) # Draw Floor

					i -= 1

		if debugsurface != None:
			debugsurface.blit(localdebugsurface, (0,0))

class Environment:
	def __init__(self):
		self.rooms = list()
		self.walls = list()
	
	def add_room(self, floor_color = (0, 0, 0), ceiling_color = (0, 0, 0)):
		self.rooms.append(Room(self, floor_color, ceiling_color))
	
	def draw_to_map(self, surface):
		for room in self.rooms:
			room.draw_to_map(surface)

class Room:
	def __init__(self, environment: Environment, floor_color, ceiling_color):
		self.environment = environment
		self.floor_color = floor_color
		self.ceiling_color = ceiling_color
		self.walls = list()
	
	def add_wall_existing(self, wall):
		self.walls.append(wall.copy(self))
	
	def add_wall_first(self, start_point, end_point, color):
		self.walls.append(Wall(self, color, start_point, end_point))
	
	def add_wall_abs(self, end_point, color):
		self.walls.append(Wall(self, color, self.walls[-1].end_point, end_point))
	
	def draw_to_map(self, surface):
		for wall in self.walls:
			wall.draw_to_map(surface)

class Wall:
	def __init__(self, room, color, start_point, end_point):
		self.start_point = start_point
		self.end_point = end_point
		self.bottom_pos = 0
		self.top_pos = wall_height
		self.color = pygame.Color(color)
		self.room = room
		self.room.environment.walls.append(self)
		self.other_side = None
	
	def copy(self, new_room):
		new_wall = Wall(new_room, self.color, self.start_point, self.end_point)
		self.other_side = new_wall
		new_wall.other_side = self
		return new_wall

	
	def draw_to_map(self, surface):
		pygame.draw.aaline(surface, self.color, self.start_point, self.end_point)

player = Player()
player.position = Vector2((8, 8))

test_env_scale = 1/12
environment = Environment()
environment.add_room(floor_color=(25, 25, 25), ceiling_color=(127, 127, 127))
environment.rooms[0].add_wall_first((100 * test_env_scale, 4 * test_env_scale), (196 * test_env_scale, 76 * test_env_scale), (237, 28, 36))
environment.rooms[0].add_wall_abs((159 * test_env_scale, 194 * test_env_scale), (255, 127, 39, 0))
environment.rooms[0].add_wall_abs((41 * test_env_scale, 194 * test_env_scale), (255, 242, 0))
environment.rooms[0].add_wall_abs((5 * test_env_scale, 76 * test_env_scale), (34, 177, 76))
environment.rooms[0].add_wall_abs((100 * test_env_scale, 4 * test_env_scale), (0, 162, 232))

environment.add_room(floor_color=(25, 60, 25), ceiling_color=(127, 180, 127))
environment.rooms[1].add_wall_existing(environment.rooms[0].walls[1])
environment.rooms[1].add_wall_abs((425 * test_env_scale, 194 * test_env_scale), (255, 201, 14))
environment.rooms[1].add_wall_abs((425 * test_env_scale, 77 * test_env_scale), (239, 228, 176, 127))
environment.rooms[1].add_wall_abs((196 * test_env_scale, 76 * test_env_scale), (181, 230, 29))

environment.add_room(floor_color=(60, 25, 25), ceiling_color=(180, 127, 127))
environment.rooms[1].add_wall_existing(environment.rooms[1].walls[2])
environment.rooms[1].add_wall_abs((425 * test_env_scale, 10 * test_env_scale), (163, 73, 164))
environment.rooms[1].add_wall_abs((471 * test_env_scale, 57 * test_env_scale), (255, 242, 0))
environment.rooms[1].add_wall_abs((512 * test_env_scale, 21 * test_env_scale), (34, 177, 76))
environment.rooms[1].add_wall_abs((564 * test_env_scale, 98 * test_env_scale), (0, 162, 232))
environment.rooms[1].add_wall_abs((588 * test_env_scale, 289 * test_env_scale), (153, 217, 234))
environment.rooms[1].add_wall_abs((425 * test_env_scale, 277 * test_env_scale), (112, 146, 190))
environment.rooms[1].add_wall_abs((425 * test_env_scale, 194 * test_env_scale), (200, 191, 231))

# Game loop
running = True
frame = 0
while running:
	# Limit the framerate
	frame_delta = clock.tick(framerate)

	# Handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			running = False
		if event.type == pygame.KEYDOWN:
			if event.key == K_c: # Hide the mouse
				pygame.mouse.set_visible(not pygame.mouse.get_visible())
				pygame.event.set_grab(not pygame.event.get_grab())
			elif event.key == K_KP_9: # Debug FOV up
				player.update_fov(vfov=player.camera_vfov_degrees + 1)
				player.print_camera_stats()
			elif event.key == K_KP_6: # Debug FOV down
				player.update_fov(vfov=player.camera_vfov_degrees - 1)
				player.print_camera_stats()
			elif event.key == K_KP_8: # Debug camera width up
				player.update_fov(distance=player.camera_distance + .1)
				player.print_camera_stats()
			elif event.key == K_KP_5: # Debug camera width down
				player.update_fov(distance=player.camera_distance - .1)
				player.print_camera_stats()
	
	mousemovement = pygame.mouse.get_rel() # Get mouse movement in this frame
	player.rotate(mousemovement[0] * .15)


	keyspressed = pygame.key.get_pressed()
	if keyspressed[K_a]: player.move(1, frame_delta, True) # Left
	if keyspressed[K_d]: player.move(-1, frame_delta, True) # Right
	if keyspressed[K_w]: player.move(1, frame_delta) # Forward
	if keyspressed[K_s]: player.move(-1, frame_delta) # Back
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