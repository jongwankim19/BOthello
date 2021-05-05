import random


class Strategy():
    def __init__(self, turn, k):
        self.k = k
        self.turn = turn
        self.numList = [str(i) for i in range(0, 64)]
        self.directions = [-9, -8, -7, -1, 1, 7, 8, 9]
        self.cx = {0: [1, 8, 9], 7: [6, 14, 15],
                   56: [48, 49, 57], 63: [54, 55, 62]}
        self.sweetSixteen = set(
            [18, 19, 20, 21, 26, 27, 28, 29, 34, 35, 36, 37, 42, 43, 44, 45])

    def makeMove(self, board, token, mv, flip):
        copied = board[:]
        for n in flip[mv]:
            copied[n] = token
        return copied

    def evalBoard(self, board, token):
        return board.count(token) - board.count(self.opposite(token))

    def opposite(self, turn):
        if turn == 'X':
            return 'O'
        return 'X'

    def changeCol(self, num):
        if num in [-7, 9, 1]:
            return 1
        if num in [7, -9, -1]:
            return -1
        return 0

    def onBoard(self, index, tempIndex):
        return 0 <= tempIndex and tempIndex <= 63

    def validMove(self, board, index, turn):
        if board[index] != '.' or not (0 <= index <= 63):
            return False
        # first, set the position temporarily
        board[index] = turn
        other = self.opposite(turn)
        # if the index is not constant or linear, then it does not work
        flip = []
        for num in self.directions:
            tempIndex = index
            col = tempIndex % 8
            tempIndex += num
            col += self.changeCol(num)
            # keep going until you find your token
            if self.onBoard(index, tempIndex) and board[tempIndex] == other and (0 <= col <= 7):
                tempIndex += num
                col += self.changeCol(num)
                if not self.onBoard(index, tempIndex) or col < 0 or col > 7:
                    continue
                if (col == 0 or col == 7) and num in [-7, 9, 1, 7, -9, -1]:
                    if board[tempIndex] == other:
                        continue
                while board[tempIndex] == other:
                    tempIndex += num
                    col += self.changeCol(num)
                    if num in [-7, 9, 1, 7, -9, -1]:
                        if col <= 0 or col >= 7:
                            break
                    if not self.onBoard(index, tempIndex):
                        break
                if not self.onBoard(index, tempIndex) or board[tempIndex] == other:
                    continue
                # print(str(index) + " " + str(tempIndex), col)
                if board[tempIndex] == turn:
                    while True:
                        tempIndex -= num
                        if tempIndex == index:
                            break
                        flip.append(tempIndex)
        # undo the filling
        board[index] = '.'
        if len(flip) == 0:
            return False
        return set(flip)

    def getMoves(self, board, turn):
        moves = []
        toFlip = {}
        for ind in range(0, 64):
            result = self.validMove(board, ind, turn)
            if result:
                moves.append(ind)
                if ind not in toFlip:
                    result.add(ind)
                    toFlip[ind] = result
                else:
                    toFlip[ind] = toFlip[ind] | result
        return moves, toFlip

    def negamaxTerminalBounded(self, board, token, improvable, hardBound, k):
        retTup = self.getMoves(board, token)
        lm, flip = retTup[0], retTup[1]
        enemy = self.opposite(token)

        if k <= 0:
            return [self.evalBoard(board, token), -4]

        if not lm:
            retTup2 = self.getMoves(board, enemy)
            lm2, flip2 = retTup2[0], retTup2[1]
            if not lm2:
                return [self.evalBoard(board, token), -3]  # -3 means game over
            nm = self.negamaxTerminalBounded(
                board, enemy, -hardBound, -improvable, k - 1) + [-1]
            return [-nm[0]] + nm[1:]
        best = []
        newHB = -improvable
        for mv in lm:
            nm = self.negamaxTerminalBounded(self.makeMove(board, token, mv, flip),
                                             enemy, -hardBound, newHB, k - 1) + [mv]
            #print(token, nm)
            if not best or nm[0] < newHB:
                best = nm
                if nm[0] < newHB:
                    newHB = nm[0]
                    # pruning
                    if -newHB >= hardBound:
                        return [-best[0]] + best[1:]
        return [-best[0]] + best[1:]

    def play(self, board):
        boardChoice = None

        # get possible moves
        retTup = self.getMoves(board, self.turn)
        posMoves, toFlip = retTup[0], retTup[1]

        if len(posMoves) > 0:
            neg = self.negamaxTerminalBounded(
                board, self.turn, -65, 65, self.k)
            boardChoice = neg[-1]

            board = self.makeMove(board, self.turn, boardChoice, toFlip)
        return board
