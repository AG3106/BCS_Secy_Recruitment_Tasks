import math

import numpy as np


def is_occupied(pos, board):
    y, x = pos
    return board[y, x] == 1
def move_left(pos, board):
    new_pos = pos[0], pos[1] - 1
    return new_pos if (0 <= new_pos[0] < board.shape[0] and 0 <= new_pos[1] < board.shape[1]
                      and not is_occupied(new_pos, board)) else pos
def move_right(pos, board):
    new_pos = pos[0], pos[1] + 1
    return new_pos if (0 <= new_pos[0] < board.shape[0] and 0 <= new_pos[1] < board.shape[1]
                      and not is_occupied(new_pos, board)) else pos
def move_down(pos, board):
    new_pos = pos[0]+1, pos[1]
    return new_pos if (0 <= new_pos[0] < board.shape[0] and 0 <= new_pos[1] < board.shape[1]
                      and not is_occupied(new_pos, board)) else pos
def move_up(pos, board):
    new_pos = pos[0] - 1, pos[1]
    return new_pos if (0 <= new_pos[0] < board.shape[0] and 0 <= new_pos[1] < board.shape[1]
                      and not is_occupied(new_pos, board)) else pos

def death_eater_move(harry_pos, pos, board):
    # BFS from self.pos → self.harry_pos
    queue   = [(pos, [])]
    visited = {pos}

    while queue:
        current_pos, path = queue.pop(0)
        if current_pos == harry_pos:
            # if we have a step to take, move there
            if len(path) > 0:
                pos = path[0]
                # print('found')
            # else: we’re already on Harry: self.pos stays the same
            return pos

        for action in [move_left, move_right, move_down, move_up]:
            next_pos = action(current_pos, board)
            if next_pos not in visited and next_pos != current_pos:
                visited.add(next_pos)
                queue.append((next_pos, path+[next_pos]))
    # no path found → stay put
    return pos

def distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

class Env:

    def __init__(self):
        self.death_eater_pos = None
        self.harry_pos = None
        self.width = 15
        self.height = 10
        self.board = np.array([
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                        [1,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
                        [1,0,1,1,0,1,0,1,0,1,1,0,0,0,1],
                        [1,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
                        [1,0,1,0,0,1,1,0,1,1,0,0,1,0,1],
                        [1,0,0,0,0,1,0,0,1,0,1,0,1,0,1],
                        [1,0,0,0,0,1,0,0,0,0,0,0,1,0,1],
                        [1,0,1,0,0,1,1,0,1,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
                        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
                    ], dtype=int)
        self.view_board = self.board.copy()
        self.score = 0
        self.actions = {
            0: 'move_left',
            1: 'move_right',
            2: 'move_down',
            3: 'move_up'
        }
        self.action_map = {
            0: move_left,
            1: move_right,
            2: move_down,
            3: move_up
        }
        self.n_actions = len(self.action_map)

        # Find all positions where the value is 0
        zero_positions = np.where(self.board == 0)
        # Convert to list of (y, x) coordinates
        self.zero_indices = list(zip(zero_positions[0], zero_positions[1]))
        self.steps = 0
    def get_state(self, pos):
        state = self.zero_indices.index(pos)
        return state

    def reset(self):
        self.steps = 0
        self.score = 0
        self.view_board = self.board.copy()
        # Randomly select three positions
        random_indices = np.random.choice(len(self.zero_indices), 3, replace=False)
        # Get the three random positions
        self.harry_pos, self.cup_pos, self.death_eater_pos = (self.zero_indices[i] for i in random_indices)
        # These are the three random indexes inside self.board which are 0
        self.h_state = random_indices[0]
        self.c_state = random_indices[1]
        self.d_state = random_indices[2]
        # self.harry_pos = (3,1)
        # self.death_eater_pos= (8,12)
        # print(self.harry_pos, self.cup_pos, self.death_eater_pos)
        self.view_board[self.harry_pos] = 2
        self.view_board[self.cup_pos] = 3
        self.view_board[self.death_eater_pos] = 4
        return self.view_board

    def step(self, action):
        self.steps += 1
        old_harry_pos = self.harry_pos
        old_distance_to_cup = distance(old_harry_pos, self.cup_pos)
        old_distance_to_de = distance(old_harry_pos, self.death_eater_pos)

        # Move Death Eater


        # Move Harry
        self.harry_pos = self.action_map[action](self.harry_pos, self.board)
        self.death_eater_pos = death_eater_move(self.harry_pos, self.death_eater_pos, self.board)
        caught = self.harry_pos == self.death_eater_pos
        reward = -1  # Small penalty per step to discourage idling

        # Wall or invalid move penalty
        if self.harry_pos == old_harry_pos:
            reward -= 5  # Stronger penalty for hitting walls

        # Cup distance reward
        new_distance_to_cup = distance(self.harry_pos, self.cup_pos)
        if new_distance_to_cup < old_distance_to_cup:
            reward += 2 * (old_distance_to_cup - new_distance_to_cup)
        elif new_distance_to_cup > old_distance_to_cup:
            reward -= 1 * (new_distance_to_cup - old_distance_to_cup)

        # Death Eater avoidance penalty
        new_distance_to_de = distance(self.harry_pos, self.death_eater_pos)
        if new_distance_to_de < old_distance_to_de:
            reward -= 2 * (old_distance_to_de - new_distance_to_de)
        elif new_distance_to_de > old_distance_to_de:
            reward += 0.5 * (new_distance_to_de - old_distance_to_de)

        win = False
        done = False
        self.view_board = self.board.copy()
        self.view_board[self.harry_pos] = 2
        self.view_board[self.cup_pos] = 3
        self.view_board[self.death_eater_pos] = 4

        if self.steps > 1000:
            reward -= 50
            done = True

        if caught or self.harry_pos == self.death_eater_pos:
            reward = -100
            self.score = 0
            done = True
        elif self.harry_pos == self.cup_pos:
            reward = 100
            self.score = 10
            done = True
            win = True

        h_state = self.get_state(self.harry_pos)
        c_state = self.get_state(self.cup_pos)
        d_state = self.get_state(self.death_eater_pos)
        return (h_state, c_state, d_state), reward, done, win

# env = Env()
# env.reset()
# print(env.board[(0), 0])