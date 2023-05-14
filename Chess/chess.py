c_king = 0
c_queen = 1
c_rook = 2
c_bishop = 3
c_knight = 4
c_pawn = 5

pieceLetters = list()
pieceLetters.append("K")
pieceLetters.append("Q")
pieceLetters.append("R")
pieceLetters.append("B")
pieceLetters.append("N")
pieceLetters.append("P")

def GenerateBoardList():
	out = list()
	i = 0
	while i < 64:
		space = dict()
		space["player"] = None # 0: White, 1: Black
		space["piece"] = None # Uses piece constants
		out.append(space)
		i += 1
	return out

def ToListCoord(inCoord): # Takes coordinates and converts them to a position in a list, starting from the bottom left corner and moving across, then up.
	if type(inCoord) == tuple:
		file = inCoord[0]
		rank = inCoord[1]
	elif type(inCoord) == str:
		inCoord = inCoord.lower()
		file = ord(inCoord[0]) - ord("a")
		rank = int(inCoord[1]) - 1
	return (rank * 8) + file

def ToNotationCoord(inCoord): # Takes coordinates and converts them to letter number notation.
	if type(inCoord) == float:
		inCoord = int(inCoord)
	if type(inCoord) != int:
		inCoord = ToListCoord(inCoord)
	
	file = chr((inCoord % 8) + ord("a"))
	rank = (inCoord // 8) + 1
	return f"{file}{rank}"

def ToTupleCoord(inCoord): # Takes coordinates and converts them to a (x, y) tuple starting from the bottom left.
	if type(inCoord) == float:
		inCoord = int(inCoord)
	if type(inCoord) != int:
		inCoord = ToListCoord(inCoord)
	
	file = inCoord % 8
	rank = inCoord // 8
	return (file, rank)

def FENreader(FENstring): # Generates a board from an FEN string. Currently only reads peice positions and colors
	board = GenerateBoardList()
	readingBoard = True
	rank = 7
	file = 0
	i = 0
	while i < len(FENstring):
		if readingBoard:
			targetchar = FENstring[i]
			piece = None
			player = None
			if targetchar == "/": # Start of next rank
				rank -= 1
				file = 0
			elif targetchar == " ":
				readingBoard = False
			else:
				if targetchar >= "0" and targetchar <= "8": # Character is number denoting empty span
					file += int(targetchar)
				elif targetchar.upper() in pieceLetters: # Character is a piece letter
					piece = pieceLetters.index(targetchar.upper())
					if targetchar >= "A" and targetchar <= "Z": # Upper case: White
						player = 0
					elif targetchar >= "a" and targetchar <= "z": # Lower case: Black
						player = 1
					boardpos = (rank * 8) + file
					board[boardpos]["piece"] = piece
					board[boardpos]["player"] = player
					file += 1
		i += 1
	return board