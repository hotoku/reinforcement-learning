#!/usr/bin/env python3

"""
マルバツの完全解析をする
"""

import itertools as it
import logging
import pickle

import click


LOGGER = logging.getLogger(__file__)


def to_str(board):
    return tuple(board[0]) + tuple(board[1]) + tuple(board[2])


def row(board, i):
    return [board[i][j] for j in range(3)]


def col(board, j):
    return [board[i][j] for i in range(3)]


def diag1(board):
    return [board[i][i] for i in range(3)]


def diag2(board):
    return [board[i][2 - i] for i in range(3)]


def win(board, player):
    for i in range(3):
        r = row(board, i)
        if len(set(r)) == 1 and r[0] == player:
            return True

    for j in range(3):
        c = col(board, j)
        if len(set(c)) == 1 and c[0] == player:
            return True

    if len(set(diag1(board))) == 1 and board[0][0] == player:
        return True

    if len(set(diag2(board))) == 1 and board[0][2] == player:
        return True

    return False


def dfs(depth, player, board, ret):
    print(depth, to_str(board))
    key = to_str(board)
    if key in ret:
        return ret[key]

    if win(board, player):
        if player == 1:
            v = 1
        else:
            v = -1
        ret[key] = v
        return v

    if depth == 9:
        if win(board, 1):
            v = 1
        elif win(board, 2):
            v = -1
        else:
            v = 0
        ret[key] = v
        return v

    values = []
    for i, j in it.product(range(3), range(3)):
        if board[i][j] == 0:
            board[i][j] = player
            values.append(dfs(depth + 1, 1 if player == 2 else 2,
                              board, ret))
            board[i][j] = 0
    if player == 1:
        ret[key] = max(values)
    else:
        ret[key] = min(values)
    return ret[key]


@click.command()
def main():
    ret = {}
    board = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0]
    ]
    dfs(0, 1, board, ret)
    pickle.dump(ret, open("ttt.pickle", "wb"))
    print(ret)


if __name__ == "__main__":
    main()
