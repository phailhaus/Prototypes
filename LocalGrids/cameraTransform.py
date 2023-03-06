import pygame

def cameraTransform(surface, inputcoord, cameraposition, camerarotation, camerascale):
	surfacesize = pygame.Vector2(surface.get_size())
	inputcoord = pygame.Vector2(inputcoord)
	cameraposition = pygame.Vector2(cameraposition)
	outputcoord = inputcoord - cameraposition
	outputcoord.rotate_ip(camerarotation * 360)
	outputcoord *= camerascale
	outputcoord += surfacesize / 2
	return outputcoord