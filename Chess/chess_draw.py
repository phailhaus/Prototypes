import chess
import pygame
from pygame.locals import *
import pygame.freetype

# Initialize Pygame
pygame.init()

# Load default font
defaultFont = pygame.freetype.Font(None, 12)

# Set screen resolution driving variables
cell_size = 128
font_size = cell_size * .9

# Set the dimensions of the screen
screen_width = cell_size * 8
screen_height = cell_size * 8
screen = pygame.display.set_mode((screen_width, screen_height))

# Initialize Clipboard Support
pygame.scrap.init()

# Set up the clock object
clock = pygame.time.Clock()
framerate = 30

# Set the title of the window
pygame.display.set_caption("Chess viewer")

c_black = (0, 0, 0)
c_white = (255, 255, 255)
c_dark = (116, 116, 116)
c_light = (140, 140, 140)

# Game loop
running = True
frame = 0
chessgame = chess.Game()
while running:
	# Limit the framerate
	clock.tick(framerate)

	# Handle events
	for event in pygame.event.get():
		if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			running = False
		if (event.type == MOUSEBUTTONDOWN and event.button == 3) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
			clipboard = str(pygame.scrap.get(SCRAP_TEXT), 'UTF-8')
			chessgame = chess.FENreader(clipboard)
	
	# Clear the screen
	screen.fill(c_dark)

	# Draw cells
	i = 0
	while i < 8:
		j = i % 2
		while j < 8:
			cellrect = pygame.Rect(j * cell_size, i * cell_size, cell_size, cell_size)
			pygame.draw.rect(screen, c_light, cellrect)
			j += 2
		i += 1
	
	# Draw pieces
	i = 0
	while i < 64:
		boardcell = chessgame.board[i]
		if boardcell["piece"] is not None:
			cellTupleCoords = chess.ToTupleCoord(i)
			cellScreenX = cellTupleCoords[0] * cell_size
			cellScreenY = (7 - cellTupleCoords[1]) * cell_size
			
			if boardcell["player"] == chess.c_playerwhite:
				cellcolor = c_white
			else:
				cellcolor = c_black

			charactertodraw = chess.pieceLetters[boardcell["piece"]]

			charmetric = defaultFont.get_metrics(charactertodraw)[0][2]
			if charmetric > 2 ** 31: # Check for unsigned int with rollover
				charmetric -= 2 ** 32 # Convert to signed int
			characterrect = defaultFont.get_rect(charactertodraw, size = font_size)
			centerx = cellScreenX + (cell_size / 2) # Center horizontally
			centery = cellScreenY + (cell_size / 2) - charmetric # Center vertically using metrics
			characterrect.center = (centerx, centery)
			defaultFont.render_to(screen, characterrect, text=None, fgcolor=cellcolor, size=font_size) # Draw character

		i += 1

	# Update the screen
	pygame.display.flip()
	frame += 1

# Clean up
pygame.quit()
