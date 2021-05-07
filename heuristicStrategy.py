# import strategy
from strategy import *
import random
import sys
class HeuristicStrategy():
    def __init__(self, turn, k ):
        self.k = k
        self.turn = turn
        self.numList = [str(i) for i in range(0, 64)]
        self.directions = [-9, -8, -7, -1, 1, 7, 8, 9]
        self.cx = {0: [1, 8, 9], 7: [6, 14, 15],
                   56: [48, 49, 57], 63: [54, 55, 62]}
        self.sweetSixteen = set(
            [18, 19, 20, 21, 26, 27, 28, 29, 34, 35, 36, 37, 42, 43, 44, 45])
        self.format = [10*i+j for i in range(1, 9) for j in range(1, 9)]

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


    def optimize(self, board, posMoves, toFlip, turn):
        if len(posMoves) == 1:
            return posMoves[0]
        good = set()
        # first optimization
        for n in [0, 7, 56, 63]:
            if n in posMoves:
                good.add(n)
        if good:
            return random.choice(list(good))
        # second optimization
        edges = [n for n in posMoves if (
            n // 8 == 0 or n // 8 == 7 or n % 8 == 0 or n % 8 == 7) and n not in [0, 7, 56, 63]]
        for num in edges:
            canFlip = toFlip[num]
            for n in [0, 7, 56, 63]:
                if n in canFlip:
                    good.add(num)
        if good:
            return random.choice(list(good))
        # third optimization
        for index in self.cx:
            if board[index] != turn:
                for num in self.cx[index]:
                    if num in posMoves:
                        posMoves.remove(num)
                        if len(posMoves) == 1:
                            return posMoves[0]
        if len(posMoves) == 0:
            return -1
        # last optimization
        for n in posMoves:
            if n // 8 == 0 or n // 8 == 7 or n % 8 == 0 or n % 8 == 7:
                posMoves.remove(n)
                if len(posMoves) == 1:
                    return posMoves[0]
        if posMoves:
            return random.choice(posMoves)
        return -1    

    def negamax(self, board, token, levels):
        retTup = self.getMoves(board, token)
        lm, flip = retTup[0], retTup[1]
        enemy = self.opposite(token)
        retTup2 = self.getMoves(board, enemy)
        lm2, flip2 = retTup2[0], retTup2[1]
        if not lm and not lm2:
            return [self.evalBoard(board, token)]
        if not lm:
            nm = self.negamax(board, enemy, levels - 1) + [-1]
            return [-nm[0]] + nm[1:]
        numList = sorted([self.negamax(self.makeMove(board, token, mv, flip),
                                enemy, levels - 1) + [mv] for mv in lm])
        best = numList[0]
        return [-best[0]] + best[1:]


    def negamaxTerminal(self, board, token, improvable, hardBound):
        retTup = self.getMoves(board, token)
        print(11)
        lm, flip = retTup[0], retTup[1]
        enemy = self.opposite(token)
        print(12)
        if not lm:
            print(13)
            retTup2 = self.getMoves(board, enemy)
            print(14)
            lm2, flip2 = retTup2[0], retTup2[1]
            if not lm2:
                print(15)
                return [self.evalBoard(board, token), -3]  # -3 means game over
            print(16)
            nm = self.negamaxTerminal(board, enemy, -hardBound, -improvable) + [-1]
            print(17)
            return [-nm[0]] + nm[1:]
        print(18)
        best = []
        newHB = -improvable
        for mv in lm:
            print(19)
            nm = self.negamaxTerminal(self.makeMove(board, token, mv, flip),
                                enemy, -hardBound, newHB) + [mv]
            print(20)
            if not best or nm[0] < newHB:
                print(21)
                best = nm
                if nm[0] < newHB:
                    print(22)
                    newHB = nm[0]
                    # pruning
                    if -newHB >= hardBound:
                        return [-best[0]] + best[1:]
        print(23)
        return [-best[0]] + best[1:]
    
    def negamaxTerminalBounded(self, board, token, improvable, hardBound, k):
        retTup = self.getMoves(board, token)
        lm, flip = retTup[0], retTup[1]
        enemy = self.opposite(token)
        # print("k: ", k)
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

        # print possible moves
        retTup = self.getMoves(board, self.turn)
        posMoves, toFlip = retTup[0], retTup[1]

        if len(posMoves) > 0:
            print(1)
            print("not :" ,bounded != 'b')
            if bounded != 'b':
                print(2)
                # preferred move by heuristic
                tempPos = posMoves[:]
                print(3)
                result = self.optimize(board, tempPos, toFlip, self.turn)
                print(4)
                if result != -1:
                    print(5)
                    boardChoice = result
                else:
                    print(6)
                    posMoves = set(posMoves)
                    intersectionSet = posMoves & self.sweetSixteen
                    if intersectionSet:
                        print(7)
                        boardChoice = random.choice(list(intersectionSet))
                    else:
                        print(8)
                        boardChoice = random.choice(posMoves)

                print("My heuristic choice is ",
                        (boardChoice // 8 + 1, boardChoice % 8 + 1))

                neg = None
                # negamax
                if board.count('.') <= self.k:
                    print(9)
                    neg = self.negamaxTerminal(board, self.turn, -65, 65)
                    print('Negamax score {} and I choose move ({}, {})'.format(
                        neg, neg[-1] // 8 + 1, neg[-1] % 8 + 1))
                    boardChoice = neg[-1]
            else:
                print(10)
                print("kk: ", self.k)
                neg = self.negamaxTerminalBounded(board, self.turn, -65, 65, self.k)
                print('Negamax score {} and I choose move ({}, {})'.format(
                    neg, neg[-1] // 8 + 1, neg[-1] % 8 + 1))
                boardChoice = neg[-1]

            board = self.makeMove(board, self.turn, boardChoice, toFlip)
        return board
