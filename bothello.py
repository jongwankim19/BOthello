import sys
import random

numList = [str(i) for i in range(0, 64)]
directions = [-9, -8, -7, -1, 1, 7, 8, 9]
cx = {0: [1, 8, 9], 7: [6, 14, 15], 56: [48, 49, 57], 63: [54, 55, 62]}
sweetSixteen = set([18, 19, 20, 21, 26, 27, 28, 29,
                    34, 35, 36, 37, 42, 43, 44, 45])


def optimize(board, posMoves, toFlip, turn):
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
    for index in cx:
        if board[index] != turn:
            for num in cx[index]:
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


def getMoves(board, turn):
    moves = []
    toFlip = {}
    for ind in range(0, 64):
        result = validMove(board, ind, turn)
        if result:
            moves.append(ind)
            if ind not in toFlip:
                result.add(ind)
                toFlip[ind] = result
            else:
                toFlip[ind] = toFlip[ind] | result
    return moves, toFlip


def validMove(board, index, turn):
    if board[index] != '.' or not (0 <= index <= 63):
        return False
    # first, set the position temporarily
    board[index] = turn
    other = opposite(turn)
    # if the index is not constant or linear, then it does not work
    flip = []
    for num in directions:
        tempIndex = index
        col = tempIndex % 8
        tempIndex += num
        col += changeCol(num)
        # keep going until you find your token
        if onBoard(index, tempIndex) and board[tempIndex] == other and (0 <= col <= 7):
            tempIndex += num
            col += changeCol(num)
            if not onBoard(index, tempIndex) or col < 0 or col > 7:
                continue
            if (col == 0 or col == 7) and num in [-7, 9, 1, 7, -9, -1]:
                if board[tempIndex] == other:
                    continue
            while board[tempIndex] == other:
                tempIndex += num
                col += changeCol(num)
                if num in [-7, 9, 1, 7, -9, -1]:
                    if col <= 0 or col >= 7:
                        break
                if not onBoard(index, tempIndex):
                    break
            if not onBoard(index, tempIndex) or board[tempIndex] == other:
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


def changeCol(num):
    if num in [-7, 9, 1]:
        return 1
    if num in [7, -9, -1]:
        return -1
    return 0


def onBoard(index, tempIndex):
    return 0 <= tempIndex and tempIndex <= 63


def evalBoard(board, token):
    return board.count(token) - board.count(opposite(token))


def makeMove(board, token, mv, flip):
    copied = board[:]
    for n in flip[mv]:
        copied[n] = token
    return copied


def negamax(board, token, levels):
    retTup = getMoves(board, token)
    lm, flip = retTup[0], retTup[1]
    enemy = opposite(token)
    retTup2 = getMoves(board, enemy)
    lm2, flip2 = retTup2[0], retTup2[1]
    if not lm and not lm2:
        return [evalBoard(board, token)]
    if not lm:
        nm = negamax(board, enemy, levels - 1) + [-1]
        return [-nm[0]] + nm[1:]
    numList = sorted([negamax(makeMove(board, token, mv, flip),
                              enemy, levels - 1) + [mv] for mv in lm])
    best = numList[0]
    return [-best[0]] + best[1:]


def negamaxTerminal(board, token, improvable, hardBound):
    retTup = getMoves(board, token)
    lm, flip = retTup[0], retTup[1]
    enemy = opposite(token)

    if not lm:
        retTup2 = getMoves(board, enemy)
        lm2, flip2 = retTup2[0], retTup2[1]
        if not lm2:
            return [evalBoard(board, token), -3]  # -3 means game over
        nm = negamaxTerminal(board, enemy, -hardBound, -improvable) + [-1]
        return [-nm[0]] + nm[1:]

    best = []
    newHB = -improvable
    for mv in lm:
        nm = negamaxTerminal(makeMove(board, token, mv, flip),
                             enemy, -hardBound, newHB) + [mv]
        if not best or nm[0] < newHB:
            best = nm
            if nm[0] < newHB:
                newHB = nm[0]
                # pruning
                if -newHB >= hardBound:
                    return [-best[0]] + best[1:]
    return [-best[0]] + best[1:]


def negamaxTerminalBounded(board, token, improvable, hardBound, k):
    retTup = getMoves(board, token)
    lm, flip = retTup[0], retTup[1]
    enemy = opposite(token)

    if k == 0:
        return [evalBoard(board, token), -4]

    if not lm:
        retTup2 = getMoves(board, enemy)
        lm2, flip2 = retTup2[0], retTup2[1]
        if not lm2:
            return [evalBoard(board, token), -3]  # -3 means game over
        nm = negamaxTerminalBounded(
            board, enemy, -hardBound, -improvable, k - 1) + [-1]
        return [-nm[0]] + nm[1:]
    best = []
    newHB = -improvable
    for mv in lm:
        nm = negamaxTerminalBounded(makeMove(board, token, mv, flip),
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


def display(board):
    boardString = ''.join(board)
    print('  12345678')
    for i in range(0, 64, 8):
        print(str(i // 8 + 1) + ' ' + boardString[i:i+8])
    # print("X : O = " + str(boardString.count('X')) + " : " + str(boardString.count('O')))


def opposite(turn):
    if turn == 'X':
        return 'O'
    return 'X'


def next(board, initial):
    if initial == 'X':
        return 'O' if sum([1 for i in board if i == '.']) % 2 else 'X'
    return 'X' if sum([1 for i in board if i == '.']) % 2 else 'O'


def getPos(pos):
    if pos in numList:
        return int(pos)
    return (int(pos[1])-1)*8+(ord(pos[0].lower())-ord('a'))


if __name__ == '__main__':
    k, bounded = 14, False
    if len(sys.argv) >= 2:
        k = int(sys.argv[1])
    if len(sys.argv) == 3:
        bounded = sys.argv[2].lower() == 'b'
    board = list(
        '...........................OX......XO...........................')
    curTurn = 'O'
    print('The player starts with O \n')

    while board.count(".") > 0:
        display(board)
        print()

        move1 = getMoves(board, curTurn)[0]
        move2 = getMoves(board, opposite(curTurn))[0]
        if len(move1) == 0 and len(move2) == 0:
            break

        if curTurn == 'O':
            # get possible moves
            retTup = getMoves(board, curTurn)
            posMoves, toFlip = retTup[0], retTup[1]
            if len(posMoves) == 0:
                print("There are no possible moves")
            else:
                posMovesOutput = [(val // 8 + 1, val % 8 + 1)
                                  for val in posMoves]
                print('Possible Moves: {}'.format(posMovesOutput))

                # user inputs
                playerTurnInput = input(
                    "State your move in this format -> row and col number seperated by comma (e.g 1,1): ")
                playerRow, playerCol = int(playerTurnInput.split(
                    ',')[0]) - 1, int(playerTurnInput.split(',')[1]) - 1

                # get the position in 1D
                playerPosition = playerRow * 8 + playerCol

                # update the board
                board = makeMove(board, curTurn, playerPosition, toFlip)
        else:
            boardChoice = None

            # print possible moves
            retTup = getMoves(board, curTurn)
            posMoves, toFlip = retTup[0], retTup[1]

            if len(posMoves) > 0:
                if not bounded:
                    # preferred move by heuristic
                    tempPos = posMoves[:]
                    result = optimize(board, tempPos, toFlip, curTurn)

                    if result != -1:
                        boardChoice = result
                    else:
                        posMoves = set(posMoves)
                        intersectionSet = posMoves & sweetSixteen
                        if intersectionSet:
                            boardChoice = random.choice(list(intersectionSet))
                        else:
                            boardChoice = random.choice(posMoves)

                    print("My heuristic choice is ",
                          (boardChoice // 8 + 1, boardChoice % 8 + 1))

                    neg = None
                    # negamax
                    if board.count('.') <= k:
                        neg = negamaxTerminal(board, curTurn, -65, 65)
                        print('Negamax score {} and I choose move ({}, {})'.format(
                            neg, neg[-1] // 8 + 1, neg[-1] % 8 + 1))
                        boardChoice = neg[-1]
                else:
                    neg = negamaxTerminalBounded(board, curTurn, -65, 65, k)
                    print('Negamax score {} and I choose move ({}, {})'.format(
                        neg, neg[-1] // 8 + 1, neg[-1] % 8 + 1))
                    boardChoice = neg[-1]

                board = makeMove(board, curTurn, boardChoice, toFlip)

        curTurn = opposite(curTurn)

        print('\nCurrent Score')
        print('O: {0}, X: {1}\n'.format(board.count('O'), board.count('X')))

    print('\nFinal Board\n')
    display(board)
    Os, Xs = board.count('O'), board.count('X')
    print('\nFinal Score\n')
    print('O: {0}, X: {1}\n'.format(Os, Xs))

    if Os > Xs:
        print('You win!')
    elif Os < Xs:
        print('BOthello wins!')
    else:
        print('Tie Game!')
