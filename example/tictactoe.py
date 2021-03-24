#!/usr/bin/env python

import logging
import click
import collections
from io import StringIO


LOGGER = logging.getLogger(__file__)

Move = collections.namedtuple("Move", "id,pos")


class Board:
    def __init__(self):
        self.buf = [
            [0] * 3,
            [0] * 3,
            [0] * 3
        ]

    def receive(self, move):
        i = move.pos // 3
        j = move.pos % 3
        self.buf[i][j] = move.id

    def __str__(self):
        sio = StringIO()
        for i in range(3):
            for j in range(3):
                if self.buf[i][j] == 0:
                    sio.write(str(i * 3 + j))
                elif self.buf[i][j] == 1:
                    sio.write("o")
                elif self.buf[i][j] == 2:
                    sio.write("x")
                else:
                    raise ValueError("bad")
            sio.write("\n")
        return sio.getvalue()

    def get(self, i, j):
        return self.buf[i][j]

    def row(self, i):
        return self.buf[i]

    def col(self, j):
        return [self.buf[i][j] for i in range(3)]

    def diag1(self, i):
        return [self.buf[i][i] for i in range(3)]

    def diag2(self, i):
        return [self.buf[i][2-i] for i in range(3)]


class Player:
    def __init__(self, id_):
        self.id = id_

    def play(self, board):
        print(board)
        pos = int(input("?: "))
        return Move(self.id, pos)


class Game:
    def __init__(self, p1, p2):
        self.board = Board()
        self.players = [p1, p2]
        self.current = 0

    def start(self):
        while True:
            p = self.players[self.current]
            move = p.play(self.board)
            self.board.receive(move)
            finish, winner = self.judge()
            if finish:
                print(f"{winner.id} wan")
                break
            self.current = (self.current + 1) % len(self.players)

    def judge(self):
        for p in self.players:
            if self.win(p):
                return True, p
        if self.draw():
            return True, -1
        return False, None

    def win(self, player):
        for i in range(3):
            if len(set(self.board.row(i))) == 1 and self.board.row(i)[0] == player.id:
                return True
        for i in range(3):
            if len(set(self.board.col(i))) == 1 and self.board.col(i)[0] == player.id:
                return True
        if len(set(self.board.diag1(i))) == 1 and self.board.diag1(i)[0] == player.id:
            return True
        if len(set(self.board.diag2(i))) == 1 and self.board.diag2(i)[0] == player.id:
            return True
        return False

    def draw(self):
        for i in range(3):
            for j in range(3):
                if self.board.get(i, j) == 0:
                    return False
        return True


@click.command()
def main():
    p1 = Player(1)
    p2 = Player(2)
    game = Game(p1, p2)
    game.start()


if __name__ == "__main__":
    main()