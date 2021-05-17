import strategy
import heuristicStrategy
import sys


def display(board):
    boardString = ''.join(board)
    print('  12345678')
    for i in range(0, 64, 8):
        print(str(i // 8 + 1) + ' ' + boardString[i:i+8])


def opposite(curTurn):
    return 'X' if curTurn == 'O' else 'O'


if __name__ == '__main__':
    k1, k2 = int(sys.argv[1]), int(sys.argv[2])
    board = list(
        '...........................OX......XO...........................')

    player1 = heuristicStrategy.Strategy('O', k1)
    player2 = strategy.Strategy('X', k2)
    curTurn = 'O'

    while board.count('.') > 0:
        display(board)
        print()

        move1 = player1.getMoves(board, curTurn)[0]
        move2 = player2.getMoves(board, opposite(curTurn))[0]
        if len(move1) == 0 and len(move2) == 0:
            break

        print('{}\'s turn\n'.format(curTurn))
        if curTurn == 'O':
            board = player1.play(board)
        else:
            board = player2.play(board)

        curTurn = opposite(curTurn)

    print('\nFinal Board\n')
    display(board)
    Os, Xs = board.count('O'), board.count('X')
    print('\nFinal Score\n')
    print('O: {0}, X: {1}\n'.format(Os, Xs))

    if Os > Xs:
        print('Player 1 (Heuristic with k = {}) wins!'.format(k1))
    elif Os < Xs:
        print('Player 2 (k = {}) wins!'.format(k2))
    else:
        print('Tie Game!')
