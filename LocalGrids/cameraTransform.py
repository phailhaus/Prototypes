import pygame

class Camera:
	def __init__(self, position = (0, 0), rotation = 0, scale = 1):
		self.position = pygame.Vector2(position)
		self.rotation = rotation
		self.scale = scale

	def move(self, x = 0, y = 0, anglerelative = True, scalerelative = True, smoothingfactor = 1):
		movementvector = pygame.Vector2(x, y)
		if anglerelative: movementvector.rotate_ip(-self.rotation * 360)
		if scalerelative: movementvector *= 1/self.scale
		if smoothingfactor == 1:
			self.position += movementvector
		elif smoothingfactor != 1:
			self.smooth(posTarget = self.position + movementvector, smoothingFactor = smoothingfactor)
	
	def rotate(self, amount, angle = True, smoothingfactor = 1):
		if angle: amount = amount / 360
		if smoothingfactor == 1:
			self.rotation += amount
		elif smoothingfactor != 1:
			self.smooth(rotTarget = self.rotation + amount, smoothingFactor = smoothingfactor)
	
	def zoom(self, amount, relative = True, smoothingfactor = 1):
		if relative: amount *= self.scale
		if smoothingfactor == 1:
			self.scale += amount
		elif smoothingfactor != 1:
			self.smooth(scaleTarget = self.scale + amount, smoothingFactor = smoothingfactor)
	
	def smooth(self, posTarget = None, rotTarget = None, scaleTarget = None, smoothingFactor = .5):
		if posTarget != None:
			posTarget = pygame.Vector2(posTarget)
			self.position = exponentialSmoothBasic(posTarget, self.position, smoothingFactor)
		
		if rotTarget != None:
			self.rotation %= 1
			rotTarget %= 1
			distance = rotTarget - self.rotation
			if distance > .5:
				self.rotation += 1
			elif distance < -.5:
				rotTarget += 1

			self.rotation = exponentialSmoothBasic(rotTarget, self.rotation, smoothingFactor)
		
		if scaleTarget != None:
			self.scale = exponentialSmoothBasic(scaleTarget, self.scale, smoothingFactor)

	def transformCoord(self, surface, inputcoord):
		surfacesize = pygame.Vector2(surface.get_size())
		inputcoord = pygame.Vector2(inputcoord)
		outputcoord = inputcoord - self.position
		outputcoord.rotate_ip(self.rotation * 360)
		outputcoord *= self.scale
		outputcoord += surfacesize / 2
		return outputcoord

def exponentialSmoothBasic(target, previous, smoothingFactor):
	return previous + smoothingFactor * (target - previous)  # Basic exponential smoothing ripped from https://en.wikipedia.org/wiki/Exponential_smoothing