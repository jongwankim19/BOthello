import sys
import heuristicStrategy
import strategy


def display(board):
    boardString = ''.join(board)
    print('  12345678')
    for i in range(0, 64, 8):
        print(str(i // 8 + 1) + ' ' + boardString[i:i+8])


def opposite(curTurn):
    return 'X' if curTurn == 'O' else 'O'


if __name__ == '__main__':
    k1, k2 = int(sys.argv[1]), int(sys.argv[2])
    # k = int(sys.argv[1])
    # k2 = 9223372036854775807
    bounded = 14
    # if len(sys.argv) == :
        
        # bounded = sys.argv[2].lower() == 'b'
    board = list(
        '...........................OX......XO...........................')

    player1 = strategy.Strategy('O', k1)
    # player2 = heuristicStrategy.Strategy('X', k2)
    player2 = heuristicStrategy.HeuristicStrategy('X', k2)
    curTurn = 'O'

    while board.count('.') > 0:
        display(board)
        print()

        move1 = player1.getMoves(board, curTurn)[0]
        move2 = player2.getMoves(board, opposite(curTurn))[0]
        print("move2: ", move2)
        if len(move1) == 0 and len(move2) == 0:
            break
        
        print('{}\'s turn\n'.format(curTurn))
        if curTurn == 'O':
            board = player1.play(board)
        else:
            print("HERE")
            board = player2.play(board, bounded)

        curTurn = opposite(curTurn)

    print('\nFinal Board\n')
    display(board)
    Os, Xs = board.count('O'), board.count('X')
    print('\nFinal Score\n')
    print('O: {0}, X: {1}\n'.format(Os, Xs))

    if Os > Xs:
        print('Player 1 (k = {}) wins!'.format(k1))
    elif Os < Xs:
        if not bounded:
            print('Player 2 (heuristic) wins!')
        else:
            print('Player 2 (heuristic, k = {}) wins!'.format(k2))
    else:
        print('Tie Game!')
