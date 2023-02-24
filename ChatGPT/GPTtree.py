import math
import random
import pygame

class Parameters:
	def __init__(self):
		self.layers = 8 # How many recursive layers should be produced
		self.splits = 3 # How many new branches should come off each branch
		self.segments = 5 # How many lines per layer
		self.segmentcountvariance = 1 # How many segments above or below self.segments to swing randomly
		self.segmentcountdrop = 2 # How much to reduce segment count each layer
		self.segmentupwardbend = -.5 # How much of the difference between parent angle and up the segment should turn
		self.segmentanglevariance = .8 # How much the segment angle should be randomized
		self.segmentlengthdrop = .0 # Multiplier to segment length compared to parent.
		self.segmentlengthvariance = 0 # Modifies segment length randomly
		self.startinglength = 40 # The length of the first line of the trunk
		self.lengthdrop = .2 # Multiplier applied to parent length when determining child length. The length is multiplied by (1 - self.lengthdrop)
		self.lengthvariance = .3 # Modifies child length randomly. The length is multiplied by (1 - random.uniform(-self.lengthvariance, self.lengthvariance))
		self.startingangle = 0 # Angle of the first line.
		self.bendangle = 50 # Angle branches distribute across
		self.bendangledrop = -.1 # Multiplicitive reduction in bendangle each layer
		self.bendanglevariance = .4 # Modifies angle randomly
		self.bendangleinheritance = 1 # How much of parent angle to inherit. Less than 1 makes branches more upright than their parent, more than 1 makes them more droopy/twisted.
		self.breakchance = .05 # Chance for a child to not be created. This creates a gap.
		self.breakafterchance = .02 # Chance for a child to have no children of its own. This creates a stub.

class Branch:
	def __init__(self, x, y, angle, length, generation):
		self.x = x
		self.y = y
		self.angle = angle
		self.length = length
		self.generation = generation
		self.child_branches = []

	def spawn_child_branches(self, parameters):
		for i in range(parameters.splits):
			angle = self.angle + ((i - (parameters.splits-1)/2) * parameters.bendangle * random.uniform(1 - parameters.bendanglevariance, 1 + parameters.bendanglevariance))
			angle *= parameters.bendangleinheritance
			length = self.length * (1 - parameters.lengthdrop) * (1 - random.uniform(-parameters.lengthvariance, parameters.lengthvariance))
			if length < 5:
				continue
			if random.random() < parameters.breakchance:
				continue
			x = self.x + length * math.sin(math.radians(angle))
			y = self.y + length * math.cos(math.radians(angle))
			new_branch = Branch(x, y, angle, length, self.generation+1)
			self.child_branches.append(new_branch)
			if random.random() > parameters.breakafterchance:
				new_branch.spawn_child_branches(parameters)

	def draw(self, surface):
		end_x = self.x + self.length * math.sin(math.radians(self.angle))
		end_y = self.y + self.length * math.cos(math.radians(self.angle))
		pygame.draw.line(surface, (255, 255, 255), (int(self.x), int(self.y)), (int(end_x), int(end_y)), max(1, int(self.length/10)))
		for child in self.child_branches:
			child.draw(surface)

class Tree:
	def __init__(self, width, height, parameters):
		pygame.init()
		self.width = width
		self.height = height
		self.parameters = parameters
		self.screen = pygame.display.set_mode((self.width, self.height))
		self.background_color = (0, 0, 0)
		self.clock = pygame.time.Clock()

	def run(self):
		trunk = Branch(self.width/2, self.height, self.parameters.startingangle, self.parameters.startinglength, 0)
		for i in range(self.parameters.layers):
			trunk.spawn_child_branches(self.parameters)
			self.draw(trunk)
			pygame.display.update()
			self.clock.tick(60)
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					return

	def draw(self, trunk):
		self.screen.fill(self.background_color)
		trunk.draw(self.screen)

parameters = Parameters()
tree = Tree(800, 600, parameters)
tree.run()