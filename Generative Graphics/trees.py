import pygame
import random

# Initialize Pygame
pygame.init()

# Set the dimensions of the screen
screen_width = 1600
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set up the clock object
clock = pygame.time.Clock()
framerate = 30

# Set the title of the window
pygame.display.set_caption("Trees!")

# Recursive data class that holds branch info and child branches
class Branch:
	def __init__(self, layer = int, length = float, angle = float):
		self.layer = layer
		self.vector = pygame.math.Vector2((0, length)).rotate(angle)
		self.angle = angle
		self.children = list()
		self.windimpact = random.uniform(1, 1.5)
	
# Generates and draws trees
class Tree:
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
		
		self.tree = Branch(0, self.startinglength, self.startingangle)
		self.verticalvector = pygame.math.Vector2((0, 1))
		self.horizontalvector = pygame.math.Vector2((1, 0))
	
	# Resets self.tree and runs generate() on it, generating a new tree
	def startgeneration(self):
		self.tree = Branch(0, self.startinglength, self.startingangle)
		self.generate(self.tree, 1)
	
	# Recursively generates a tree of branches
	def generate(self, parentbranch = Branch, segment = None):
		parentlayer = parentbranch.layer
		parentlength = parentbranch.vector.length()
		parentangle = parentbranch.angle

		currentsegments = self.segments - (self.segmentcountdrop * parentlayer)
		currentsegments = round(currentsegments + (((random.random() * 2) - 1) * self.segmentcountvariance))

		if segment != None and segment < currentsegments-1:
			childlayer = parentlayer
			childlength = parentlength * (1 - self.segmentlengthdrop) * (1 - random.uniform(-self.segmentlengthvariance, self.segmentlengthvariance))
			childangle = (parentangle - (parentangle * self.segmentupwardbend)) * (1 - random.uniform(-self.segmentanglevariance, self.segmentanglevariance))
			childbranch = Branch(childlayer, childlength, childangle)
			parentbranch.children.append(childbranch)
			self.generate(childbranch, segment + 1)
		else:		
			childlayer = parentlayer + 1
			childbendangle = self.bendangle * ((1 - self.bendangledrop) ** (childlayer - 1)) # Calculate angle children should be distributed across.

			for i in range(self.splits):
				if random.random() < self.breakchance:
					pass
				else:
					childlength = parentlength * (1 - self.lengthdrop) * (1 - random.uniform(-self.lengthvariance, self.lengthvariance))
					if self.splits == 1:
						childangle = 0
					elif self.splits == 2:
						childangle = ((i * 2) - 1) * childbendangle / 2
					else:
						childangle = ((i - ((self.splits - 1) / 2)) * (childbendangle / (self.splits - 1))) # Distribute branches
					childangle += parentangle * self.bendangleinheritance # Inherit parent angle
					childangle *= 1 - random.uniform(-self.bendanglevariance, self.bendanglevariance) # Randomize angle

					childbranch = Branch(childlayer, childlength, childangle)
					parentbranch.children.append(childbranch)
					if childlayer < self.layers - 1 and random.random() > self.breakafterchance:
						self.generate(childbranch, 0)
	
	# Runs self.drawbranch on self.tree
	def draw(self, surface = pygame.surface, position = tuple, color = (255, 255, 255), angle = 0):
		self.drawbranch(self.tree, surface, position, color, angle)
	
	# Recursively draws the tree at the specified location. Bends it based on the provided angle to simulate wind. The Y coordinate is flipped when drawing.
	def drawbranch(self, branch = Branch, surface = pygame.surface, position = tuple, color = (255, 255, 255), angle = 0):
		start_pos = pygame.math.Vector2(position)
		reflectedbranchvector = pygame.math.Vector2((branch.vector.x, -branch.vector.y)) # Flip Y coordinate
		reflectedbranchvector.rotate_ip(angle * ((branch.layer + 1.5) / 1.5) * branch.windimpact) # Apply wind
		end_pos = start_pos + reflectedbranchvector
		pygame.draw.aaline(surface, color, start_pos, end_pos)
		for childbranch in branch.children:
			self.drawbranch(childbranch, surface, end_pos, color, angle = angle)

trees = list()
sparsefractaltree = Tree()
trees.append(sparsefractaltree)
defaulttree = Tree()
trees.append(defaulttree)
skinnytree = Tree()
trees.append(skinnytree)
regulartree = Tree()
trees.append(regulartree)

sparsefractaltree.layers = 5 # How many recursive layers should be produced
sparsefractaltree.splits = 6 # How many new branches should come off each branch
sparsefractaltree.segments = 1 # How many lines per layer
sparsefractaltree.segmentcountvariance = 0 # How many segments above or below self.segments to swing randomly
sparsefractaltree.segmentcountdrop = 0 # How much to reduce segment count each layer
sparsefractaltree.segmentupwardbend = 0 # How much of the difference between parent angle and up the segment should turn
sparsefractaltree.segmentanglevariance = 0 # How much the segment angle should be randomized
sparsefractaltree.segmentlengthdrop = 0 # Multiplier to segment length compared to parent.
sparsefractaltree.segmentlengthvariance = 0 # Modifies segment length randomly
sparsefractaltree.startinglength = 250 # The length of the first line of the trunk
sparsefractaltree.lengthdrop = .6 # Multiplier applied to parent length when determining child length. The length is multiplied by (1 - self.lengthdrop)
sparsefractaltree.lengthvariance = 0 # Modifies child length randomly. The length is multiplied by (1 - random.uniform(-self.lengthvariance, self.lengthvariance))
sparsefractaltree.startingangle = 0 # Angle of the first line.
sparsefractaltree.bendangle = 180 # Angle branches distribute across
sparsefractaltree.bendangledrop = 0 # Multiplicitive reduction in bendangle each layer
sparsefractaltree.bendanglevariance = 0 # Modifies angle randomly
sparsefractaltree.bendangleinheritance = 1 # How much of parent angle to inherit. Less than 1 makes branches more upright than their parent, more than 1 makes them more droopy/twisted.
sparsefractaltree.breakchance = 0 # Chance for a child to not be created. This creates a gap.
sparsefractaltree.breakafterchance = 0 # Chance for a child to have no children of its own. This creates a stub.

skinnytree.layers = 8 # How many recursive layers should be produced
skinnytree.splits = 3 # How many new branches should come off each branch
skinnytree.segments = 1 # How many lines per layer
skinnytree.segmentcountvariance = 0 # How many segments above or below self.segments to swing randomly
skinnytree.segmentcountdrop = 0 # How much to reduce segment count each layer
skinnytree.segmentupwardbend = 0 # How much of the difference between parent angle and up the segment should turn
skinnytree.segmentanglevariance = 0 # How much the segment angle should be randomized
skinnytree.segmentlengthdrop = 0 # Multiplier to segment length compared to parent.
skinnytree.segmentlengthvariance = 0 # Modifies segment length randomly
skinnytree.startinglength = 100 # The length of the first line of the trunk
skinnytree.lengthdrop = .3 # Multiplier applied to parent length when determining child length. The length is multiplied by (1 - self.lengthdrop)
skinnytree.lengthvariance = .5 # Modifies child length randomly. The length is multiplied by (1 - random.uniform(-self.lengthvariance, self.lengthvariance))
skinnytree.startingangle = 0 # Angle of the first line.
skinnytree.bendangle = 20 # Angle branches distribute across
skinnytree.bendangledrop = -.2 # Multiplicitive reduction in bendangle each layer
skinnytree.bendanglevariance = .2 # Modifies angle randomly
skinnytree.bendangleinheritance = 1.5 # How much of parent angle to inherit. Less than 1 makes branches more upright than their parent, more than 1 makes them more droopy/twisted.
skinnytree.breakchance = .1 # Chance for a child to not be created. This creates a gap.
skinnytree.breakafterchance = .02 # Chance for a child to have no children of its own. This creates a stub.

regulartree.layers = 7 # How many recursive layers should be produced
regulartree.splits = 4 # How many new branches should come off each branch
regulartree.segments = 1 # How many lines per layer
regulartree.segmentcountvariance = 0 # How many segments above or below self.segments to swing randomly
regulartree.segmentcountdrop = 0 # How much to reduce segment count each layer
regulartree.segmentupwardbend = 0 # How much of the difference between parent angle and up the segment should turn
regulartree.segmentanglevariance = 0 # How much the segment angle should be randomized
regulartree.segmentlengthdrop = 0 # Multiplier to segment length compared to parent.
regulartree.segmentlengthvariance = 0 # Modifies segment length randomly
regulartree.startinglength = 100 # The length of the first line of the trunk
regulartree.lengthdrop = .3 # Multiplier applied to parent length when determining child length. The length is multiplied by (1 - self.lengthdrop)
regulartree.lengthvariance = 0 # Modifies child length randomly. The length is multiplied by (1 - random.uniform(-self.lengthvariance, self.lengthvariance))
regulartree.startingangle = 0 # Angle of the first line.
regulartree.bendangle = 90 # Angle branches distribute across
regulartree.bendangledrop = 0 # Multiplicitive reduction in bendangle each layer
regulartree.bendanglevariance = 0 # Modifies angle randomly
regulartree.bendangleinheritance = 1 # How much of parent angle to inherit. Less than 1 makes branches more upright than their parent, more than 1 makes them more droopy/twisted.
regulartree.breakchance = 0 # Chance for a child to not be created. This creates a gap.
regulartree.breakafterchance = 0 # Chance for a child to have no children of its own. This creates a stub.

for tree in trees:
	tree.startgeneration()

bendangle = 0
targetbendangle = 30

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
		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_SPACE:
				for tree in trees:
					tree.startgeneration()

	# Clear the screen
	screen.fill((0, 0, 0))

	if frame % 15 == 0:
		targetbendangle += random.randint(-15, 15)
		if targetbendangle > 30: targetbendangle = 15
		elif targetbendangle < -30: targetbendangle = -15
	
	bendangle += (targetbendangle - bendangle) / 60

	# Draw the trees
	for i in range(len(trees)):
		trees[i].draw(screen, ((((screen_width * .66) / (len(trees)-1)) * i) + (screen_width * .1666), screen_height - 10), angle=bendangle)

	# Update the screen
	pygame.display.flip()
	frame += 1

# Clean up
pygame.quit()