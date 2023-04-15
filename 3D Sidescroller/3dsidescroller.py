import pygame
from pygame.math import Vector2
from pygame.locals import *
import pygame.freetype
import random

# Initialize Pygame
pygame.init()

# Load default font
defaultFont = pygame.freetype.Font(None, 12)

# Set the dimensions of the screen
screen_width = 1600
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the world bounds
worldsize = 100

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
	
	def move(self, distance, normal = False):
		movementvector = self.angle.rotate(-90 * normal)
		movementvector.scale_to_length(distance)
		self.position = self.position + movementvector
	
	def rotate(self, rotation):
		self.angle.rotate_ip(rotation)

# World Object Handler
class WorldObject:
	def __init__(self, object):
		self.object = object
		self.screenposition = None
	
	def updateScreenPosition(self, cameraposition, cameraangle):
		self.screenposition = self.object.position - cameraposition # Shift world so that camera is at zero
		self.screenposition = self.screenposition.rotate(-cameraangle.as_polar()[1]) # Rotate world to camera angle
		self.screenposition.y = -self.screenposition.y

	def draw(self, surface, targetrect):
		self.object.draw(surface, targetrect, self.screenposition)
		
class DebugTextObject:
	def __init__(self, position, color):
		self.position = Vector2(position)
		self.color = color
	
	def draw(self, surface, targetrect, screenposition):
		# Map
		xsurface, xrect = defaultFont.render(f"X: {screenposition.x:.2f}", self.color, None)
		xrect.midbottom = self.position * 8
		xrect.y -= 5
		surface.blit(xsurface, xrect)
		ysurface, yrect = defaultFont.render(f"Y: {screenposition.y:.2f}", self.color, None)
		yrect.midtop = self.position * 8
		yrect.y += 5
		surface.blit(ysurface, yrect)
		pygame.draw.circle(surface, self.color, self.position * 8, 3)
		
		# Camera
		if -50 < screenposition.x < 50 and -10 < screenposition.y:
			distancescalar = screenposition.y / (worldsize / 2) # Make distance value proportional to half of map size
			viewwidth = distancescalar * 40 # Make the width 0-40 instead of 0-1
			viewwidth += 10 # Make the width 10-50

			renderpositionx = screenposition.x / viewwidth # Gives a centered scalar of screen position based on depth			
			renderpositionx *= 400 # Make it -400-+400
			renderpositionx += 1200 # Make it 800-1600
			if 800 < renderpositionx < 1600:
				pygame.draw.circle(surface, self.color, (renderpositionx, 400 + (distancescalar * 20)), (20 * (1-distancescalar)) + 20)
				

player = Player()
player.position = Vector2((50, 50))


worldObjectList = list()

for i in range(10):
	worldObjectList.append(WorldObject(DebugTextObject((i * 8 + 10, 15), (255, 25 * i, 0))))
	worldObjectList.append(WorldObject(DebugTextObject((i * 8 + 10, 20), (0, 255, 25 * i))))

for i in range(100):
	randx = (random.random() * 90)
	randy = (random.random() * 40) + 50
	worldObjectList.append(WorldObject(DebugTextObject((randx, randy), (127 + (random.random() * 128), 127 + (random.random() * 128), 127 + (random.random() * 128)))))

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
	player.rotate(mousemovement[0] * .1)


	keyspressed = pygame.key.get_pressed()
	if keyspressed[K_a]: player.move(-.5) # Left
	if keyspressed[K_d]: player.move(.5) # Right
	if keyspressed[K_w]: player.move(.5, True) # Forward
	if keyspressed[K_s]: player.move(-.5, True) # Back
	if keyspressed[K_q]: player.rotate(-1) # Rotate counter-clockwise
	if keyspressed[K_e]: player.rotate(1) # Rotate clockwise

	# Update screen positions
	sortedWorldObjectList = list()
	for thing in worldObjectList:
		thing.updateScreenPosition(player.position, player.angle)
		sortedWorldObjectList.append((thing.screenposition.y, thing))

	sortedWorldObjectList.sort(key=lambda tup: tup[0], reverse=True)


	# Clear the screen
	screen.fill((0, 0, 0))

	# Top-down display
	surface = pygame.Surface((screen_width, screen_height))
	scaledposition = player.position * 8 # Scale from 100x100 space to screen size
	lineoffset = Vector2(player.angle)
	lineoffset.scale_to_length(-100)
	lineredpoint = scaledposition + lineoffset
	linegreenpoint = scaledposition + lineoffset.rotate(180)
	linewhitepoint = scaledposition + lineoffset.rotate(90)
	pygame.draw.aaline(surface, (255, 0, 0), scaledposition, lineredpoint)
	pygame.draw.aaline(surface, (0, 255, 0), scaledposition, linegreenpoint)
	pygame.draw.aaline(surface, (255, 255, 255), scaledposition, linewhitepoint)
	pygame.draw.circle(surface, (255, 255, 255), scaledposition, 10)
	for thingtuple in sortedWorldObjectList:
		thingtuple[1].draw(surface, None)

	# Draw surfaces
	screen.blit(surface, (0, 0))
	pygame.draw.line(screen, (255, 255, 255), (800, 0), (800, 800), 2)

	# Update the screen
	pygame.display.flip()
	frame += 1

# Clean up
pygame.quit()