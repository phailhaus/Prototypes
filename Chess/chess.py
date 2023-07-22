c_playerwhite = 0
c_playerblack = 1

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

class Game:
	def __init__(self):
		self.board = GenerateBoardList()
		self.active_player = c_playerwhite
		self.castling_available = ((True, True), (True, True)) # (White Kingside, White Queenside), (Black Kingside, Black Queenside)
		self.legal_moves = list()
	
	def GenerateLegalMoves(self):
		self.legal_moves = list()
		king_locations = list((None, None))
		king_potential_moves = (list(), list())
		threatens_king_if_moved = (list(), list())
		protects_king_if_blocked = (list(), list())

		file=0 # King pass - Determine where the kings are and can move
		while file < 8:
			rank = 0
			while rank < 8:
				currentspacecoord = ToListCoord((file, rank))
				currentspace = self.board[currentspacecoord]

				if currentspace.piece == c_king:
					king_locations[currentspace.player] = currentspacecoord
					
					fileoffset = -1
					while fileoffset <= 1:
						targetfile = file + fileoffset
						rankoffset = -1
						while rankoffset <= 1:
							targetrank = rank + rankoffset
							if 0 <= targetfile < 8 and 0 <= targetrank < 8: # Target space is on the board
								targetcoord = ToListCoord((targetfile, targetrank))
								targetspace = self.board[targetcoord]
								if targetspace.player != currentspace.player: # Target space is empty or opposing
									king_potential_moves[currentspace.player].append(targetcoord)
							rankoffset += 1
						fileoffset += 1

				rank += 1
			file += 1

		file=0
		while file < 8:
			rank = 0
			while rank < 8:
				currentspacecoord = ToListCoord((file, rank))
				currentspace = self.board[currentspacecoord]

				if currentspace.piece == c_queen:
					searchdepth = 0
					while searchdepth < 2:
						pass
				elif currentspace.piece == c_rook:
					pass
				elif currentspace.piece == c_bishop:
					pass
				elif currentspace.piece == c_knight:
					pass
				elif currentspace.piece == c_pawn:
					pass


				rank += 1
			file += 1

class BoardSpace:
	def __init__(self):
		self.player = None # 0: White, 1: Black
		self.piece = None # Uses piece constants

def GenerateBoardList():
	out = list()
	i = 0
	while i < 64:
		out.append(BoardSpace())
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
	game = Game()
	board = game.board
	readingBoard = True
	rank = 7
	file = 0
	i = 0
	while i < len(FENstring) and readingBoard:
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
					player = c_playerwhite
				elif targetchar >= "a" and targetchar <= "z": # Lower case: Black
					player = c_playerblack
				boardpos = (rank * 8) + file
				board[boardpos].piece = piece
				board[boardpos].player = player
				file += 1
		i += 1
	activeplayer_pos = FENstring.find(" ") + 1
	castling_pos = FENstring.find(" ", activeplayer_pos) + 1
	enpassant_pos = FENstring.find(" ", castling_pos) + 1

	if FENstring[activeplayer_pos] == "w":
		game.active_player = c_playerwhite
	elif FENstring[activeplayer_pos] == "b":
		game.active_player = c_playerblack
	
	castlingstring = FENstring[castling_pos:enpassant_pos-2]
	castling_list = list((False, False, False, False))
	if "K" in castlingstring:
		castling_list[0] = True
	if "Q" in castlingstring:
		castling_list[1] = True
	if "k" in castlingstring:
		castling_list[2] = True
	if "q" in castlingstring:
		castling_list[3] = True

	game.castling_available = ((castling_list[0], castling_list[1]), (castling_list[2], castling_list[3]))
		
	return game