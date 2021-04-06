#!/usr/bin/env python

import logging
import click
import collections
from io import StringIO
import pickle
import itertools as it

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
        return [self.buf[i][2 - i] for i in range(3)]

    def to_str(self):
        return tuple(self.buf[0]) + tuple(self.buf[1]) + tuple(self.buf[2])

    def __getitem__(self, i):
        return self.row(i)


class Player:
    def __init__(self, id_):
        self.id = id_

    def play(self, board):
        raise NotImplementedError("Player.play")


class UserPlayer(Player):
    def play(self, board):
        print(board)
        pos = int(input("?: "))
        return Move(self.id, pos)


class PerfectPlayer(Player):
    def __init__(self, id_, first):
        super(PerfectPlayer, self).__init__(id_)
        with open("ttt.pickle", "rb") as f:
            self.dic = pickle.load(f)
            self.first = first

    def play(self, board):
        vs = []
        for i, j in it.product(range(3), range(3)):
            if board.get(i, j) == 0:
                board[i][j] = self.id
                vs.append((self.dic[board.to_str()], (i, j)))
                board[i][j] = 0
        vs2 = sorted(vs, key=lambda x: x[0], reverse=self.first)
        i, j = vs2[0][1]
        pos = i * 3 + j
        return Move(self.id, pos)


class Rule:
    @staticmethod
    def win(board, pid):
        for i in range(3):
            if (len(set(board.row(i))) == 1 and
                    board.row(i)[0] == pid):
                return True
        for i in range(3):
            if (len(set(board.col(i))) == 1 and
                    board.col(i)[0] == pid):
                return True
        if (len(set(board.diag1(i))) == 1 and
                board.diag1(i)[0] == pid):
            return True
        if (len(set(board.diag2(i))) == 1 and
                board.diag2(i)[0] == pid):
            return True
        return False

    @staticmethod
    def draw(board):
        for p in [1, 2]:
            if Rule.win(p):
                return False

        for i, j in it.product(range(3), range(3)):
            if board.get(i, j) == 0:
                return False
        return True


class LearningPlayer(Player):
    def __init__(self, id_, first):
        super(LearningPlayer, self).__init__(id_)
        self.enemy = 1 if self.id == 1 else 2
        self.dic = {}
        self.first = first
        self.init_dic()

    def init_dic(self):
        board = Board()

        def dfs(depth):
            if depth == 10:
                return
            if Rule.win(board, self.id):
                self.dic[str(board)] = 1
            elif Rule.win(board, self.enemy):
                self.dic[str(board)] = -1
            else:
                self.dic[str(board)] = 0.5


class Game:
    class NotFinished(Exception):
        pass

    def __init__(self, p1, p2):
        self.board = Board()
        self.players = [p1, p2]
        self.current = 0

    def next(self):
        p = self.players[self.current]
        move = p.play(self.board)
        self.board.receive(move)
        self.current = (self.current + 1) % len(self.players)

    def finished(self):
        for p in self.players:
            if self.win(p):
                return True
        if self.draw():
            return True
        return False

    def result(self):
        if not self.finished():
            raise Game.NotFinished()
        for p in self.players:
            if self.win(p):
                return p.id
        return 0


class Processor:
    def __init__(self, game):
        self.game = game

    def play(self):
        while not self.game.finished():
            self.game.next()
        ret = self.game.result()
        if ret == 0:
            print("draw")
        else:
            print(f"{ret} win")


@click.command()
def main():
    p1 = PerfectPlayer(1, True)
    p2 = UserPlayer(2)
    game = Game(p1, p2)
    proc = Processor(game)
    proc.play()


if __name__ == "__main__":
    main()
