import json
import random

from client import Client


class NoughtsAndCrossesClient(Client):
    next_step = []
    def play_game(self):
        round_count = 0
        while True:
            message = self.recv()
            if not message:
                return

            state = message.get('state')
            next_player = state.get('nextPlayer')
            complete = state.get('complete')
            if complete:
                print state['victor']
            if next_player == self.bot_id:
                updated_state = self.update_state(state, round_count)
                self.send(updated_state)
                round_count += 1

    def update_state(self, state, round_count):
        board = state.get('board')
        mark = [k for k,v in state['marks'].items() if v == self.bot_id][0]
        space = self.find_space(board, mark, round_count)
        if round_count == 0:
            print 'My mark:' + mark
        print space
        return {'space': space, 'mark': mark}

    def find_space(self, board, mark, round_count):
        result = self.find_risk_and_opportunity(board)
        print board

        if result:
            print "Rist found"
            return result

        if self.next_step:
            next_step = self.next_step
            self.next_step = []
            print "Using Next Step: "
            print next_step
            return next_step

        if self.is_first_turn(mark):
            result = self.first_turn_strategy(board, mark, round_count)
        else:
            result = self.second_turn_strategy(board, mark, round_count)

        if result:
            return result

        return self.random_strategy(board)


    def is_first_turn(self, mask):
        return True if mask == 'X' else False


    def first_turn_strategy(self, board, mark, round_count):
        print "Using first_turn_strategy"
        # Play your first X in a corner.
        if round_count == 0:
            print "Round 1: X corner"
            return [2, 0]
        elif round_count == 1:
            # Try to win if your opponent plays the first O in the center.
            if self.is_opponent(board, 1, 1, mark):
                self.next_step = [2, 2]
                print "Round 2: O center"
                return [0, 2]
            # Win automatically if your opponent plays his first O in any square besides the center.
            if self.is_opponent(board, 0, 1, mark):
                self.next_step = [1, 1]
                print "Round 2: O 0,1"
                return [0, 0]
            # Win automatically if your opponent plays his first O in any square besides the center.
            if self.is_opponent(board, 1, 2, mark):
                self.next_step = [1, 1]
                print "Round 2: O 1,2"
                return [2, 2]
        return []


    def second_turn_strategy(self, board, mark, round_count):
        print "Using second_turn_strategy"
        if round_count == 0:
            # Force a draw if the opponent starts in the corner.
            if self.is_opponent(board, 0, 0, mark) or self.is_opponent(board, 0, 2, mark) or \
                     self.is_opponent(board, 2, 0, mark) or self.is_opponent(board, 2, 2, mark):
                print "Round 1: O corner"
                return [1, 1]
            # Force a draw when the opponent starts in the center.
            if self.is_opponent(board, 1, 1, mark):
                print "Round 1: O center"
                return [2, 0]
        return []


    def random_strategy(self, board):
        print "Using random_strategy"
        i = 0
        while i < 10000:
            space = (random.randrange(3), random.randrange(3))
            if not board[space[0]][space[1]]:
                break
            i += 1
        return space


    def is_opponent(self, board, i, j, mark):
        return True if board[i][j] and board[i][j] != mark else False


    def find_risk_and_opportunity(self, board):
        for x in range(3):
            for y in range(3):
                for i in range(2-x):
                    if board[x][y] == board[x+i+1][y] != '':
                        value = x + x + i + 1
                        if board[abs(value - 3)][y]=='':
                            return [abs(value - 3), y]
                for j in range(2-y):
                    if board[x][y] == board[x][y+j+1] != '':
                        value = y + y + j + 1
                        if board[x][abs(value - 3)]=='':
                            return [x, abs(value - 3)]
                if x == y:
                    for i in range(2-x):
                        if board[x][y] == board[x+i+1][y+i+1] != '':
                            value = x + x + i + 1
                            if board[abs(value - 3)][abs(value - 3)]=='':
                                return [abs(value - 3), abs(value - 3)]
                if (x+y) == 2:
                    for i in range(2-x):
                        if board[x][y] == board[x+i+1][y-i-1] != '':
                            value = x + x + i
                            if board[2-value][value]=='':
                                return [2-value, value]

        return False


if __name__ == '__main__':
    NoughtsAndCrossesClient()
