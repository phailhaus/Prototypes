import pygame

class Camera:
	def __init__(self, position = (0, 0), rotation = 0, scale = 1):
		self.position = pygame.Vector2(position)
		self.rotation = rotation
		self.scale = scale

	def move(self, x = 0, y = 0, anglerelative = True, scalerelative = True):
		movementvector = pygame.Vector2(x, y)
		if anglerelative: movementvector.rotate_ip(-self.rotation * 360)
		if scalerelative: movementvector *= 1/self.scale
		self.position += movementvector
	
	def rotate(self, amount, angle = True):
		if angle: amount = amount / 360
		self.rotation += amount
	
	def zoom(self, amount, relative = True):
		if relative: amount *= self.scale
		self.scale += amount

	def transformCoord(self, surface, inputcoord):
		surfacesize = pygame.Vector2(surface.get_size())
		inputcoord = pygame.Vector2(inputcoord)
		outputcoord = inputcoord - self.position
		outputcoord.rotate_ip(self.rotation * 360)
		outputcoord *= self.scale
		outputcoord += surfacesize / 2
		return outputcoord