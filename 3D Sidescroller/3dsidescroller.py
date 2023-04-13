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
	
	def move(self, distance):
		movementvector = Vector2(self.angle)
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
		return self.screenposition

	def draw(self, surface, targetrect):
		self.object.draw(surface, targetrect, self.screenposition)
		
class DebugTextObject:
	def __init__(self, position, color):
		self.position = Vector2(position)
		self.color = color
	
	def draw(self, surface, targetrect, screenposition):
		xsurface, xrect = defaultFont.render(f"X: {screenposition.x:.2f}", self.color, None)
		xrect.midbottom = self.position * 8
		xrect.y -= 5
		surface.blit(xsurface, xrect)
		ysurface, yrect = defaultFont.render(f"Y: {screenposition.y:.2f}", self.color, None)
		yrect.midtop = self.position * 8
		yrect.y += 5
		surface.blit(ysurface, yrect)
		pygame.draw.circle(surface, self.color, self.position * 8, 3)



player = Player()
player.position = Vector2((50, 50))


worldObjectList = list()

redText = DebugTextObject((25,25), (255, 0, 0))
redTextWorld = WorldObject(redText)
worldObjectList.append(redTextWorld)

greenText = DebugTextObject((75,25), (0, 255, 0))
greenTextWorld = WorldObject(greenText)
worldObjectList.append(greenTextWorld)


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
	
	keyspressed = pygame.key.get_pressed()
	if keyspressed[K_a]: player.move(-.5) # Left
	if keyspressed[K_d]: player.move(.5) # Right
	if keyspressed[K_q]: player.rotate(-1) # Rotate counter-clockwise
	if keyspressed[K_e]: player.rotate(1) # Rotate clockwise

	# Update screen positions
	for thing in worldObjectList:
		thing.updateScreenPosition(player.position, player.angle)

	# Clear the screen
	screen.fill((0, 0, 0))

	# Top-down display
	leftsurface = pygame.Surface((800, 800))
	scaledposition = player.position * 8 # Scale from 100x100 space to screen size
	lineoffset = Vector2(player.angle)
	lineoffset.scale_to_length(-1000)
	lineredpoint = scaledposition + lineoffset
	lineoffset.scale_to_length(-1000)
	linegreenpoint = scaledposition + lineoffset
	pygame.draw.aaline(leftsurface, (255, 0, 0), scaledposition, lineredpoint)
	pygame.draw.aaline(leftsurface, (0, 255, 0), scaledposition, linegreenpoint)
	pygame.draw.circle(leftsurface, (255, 255, 255), scaledposition, 10)
	for thing in worldObjectList:
		thing.draw(leftsurface, None)

	# Draw surfaces
	screen.blit(leftsurface, (0, 0))
	pygame.draw.line(screen, (255, 255, 255), (800, 0), (800, 800), 2)

	# Update the screen
	pygame.display.flip()
	frame += 1

# Clean up
pygame.quit()