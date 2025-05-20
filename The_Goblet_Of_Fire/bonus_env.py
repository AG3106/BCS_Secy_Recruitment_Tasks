import numpy as np
from collections import deque

def is_occupied(pos, board):
    y, x = pos
    return board[y, x] == 1 # returns true if occupied by walls else returns false

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

def death_eater_move(harry_pos, pos, cup_pos, board):
    # Breadth First Search (BFS) algorithm applied to move death eater
    queue   = deque([(pos, [])]) # double-ended queue
    visited = {pos}

    while queue:
        current_pos, path = queue.popleft()

        if current_pos == harry_pos: # if death eater has reached to harry
            if len(path) > 0: # path is not empty
                pos = path[0]
                # print('path found')
            return pos

        for action in [move_left, move_right, move_down, move_up]: # iterating over all available actions
            next_pos = action(current_pos, board)
            if next_pos not in visited and next_pos != current_pos and next_pos != cup_pos:
                visited.add(next_pos)
                queue.append((next_pos, path+[next_pos]))
    return pos

def distance(pos1, pos2):
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) # manhattan distance

class Env:

    def __init__(self):
        self.death_eater_pos1 = None
        self.death_eater_pos2 = None
        self.harry_pos = None
        self.width = 15
        self.height = 10
        board = np.array([
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ], dtype=int)

        # Remove the central column (column index 10 in a 15-column array)

        # Concatenate the board with itself horizontally
        joined_board = np.concatenate([board, board[::-1]], axis=1)
        joined_board = np.delete(joined_board, 14, axis=1)
        joined_board = np.delete(joined_board, 14, axis=1)

        self.board = joined_board
        self.view_board = self.board.copy() # used for rendering

        # assigns integer to actions
        # simplifies action selection
        self.action_map = {
            0: move_left,
            1: move_right,
            2: move_down,
            3: move_up
        }
        self.n_actions = len(self.action_map)

        # zero indices are all possible states for death eater, harry, cup
        # this reduces no. of states from 150 to 80 in the current map
        # increasing efficiency in calculating q table
        zero_positions = np.where(self.board == 0)
        self.zero_indices = list(zip(zero_positions[0], zero_positions[1]))

        self.steps = 0 # no. of steps played in an episode

    def get_state(self, pos):
        # converts position to state according to the zero-indices list
        state = self.zero_indices.index(pos)
        return state

    def reset(self):
        # resets the env
        # also used to initialize env
        self.steps = 0
        self.view_board = self.board.copy()

        # generating positions of harry, cup, death eater
        random_indices = np.random.choice(len(self.zero_indices), 4, replace=False)
        self.harry_pos, self.cup_pos, self.death_eater_pos1, self.death_eater_pos2 = (self.zero_indices[i] for i in random_indices)

        d_to_de1 = distance(self.harry_pos, self.death_eater_pos1)
        d_to_de2 = distance(self.harry_pos, self.death_eater_pos2)
        de_min = None
        if d_to_de1 < d_to_de2:
            de_min = self.death_eater_pos1
        else:
            de_min = self.death_eater_pos2

        # generating state of harry, cup, death eater
        self.h_state = random_indices[0]
        self.c_state = random_indices[1]
        self.d_state = self.get_state(de_min)

        self.view_board[self.harry_pos] = 2
        self.view_board[self.cup_pos] = 3
        self.view_board[self.death_eater_pos1] = 4
        self.view_board[self.death_eater_pos2] = 4

        return self.view_board

    def step(self, action):
        self.steps += 1
        old_harry_pos = self.harry_pos
        old_d_to_cup = distance(old_harry_pos, self.cup_pos)
        old_d_to_de1 = distance(old_harry_pos, self.death_eater_pos1)
        old_d_to_de2 = distance(old_harry_pos, self.death_eater_pos2)
        old_d_to_de = min(old_d_to_de1, old_d_to_de2)

        # move Harry first
        self.harry_pos = self.action_map[action](self.harry_pos, self.board)
        # then move Death Eater
        self.death_eater_pos1 = death_eater_move(self.harry_pos, self.death_eater_pos1, self.cup_pos, self.board)
        self.death_eater_pos2 = death_eater_move(self.harry_pos, self.death_eater_pos2, self.cup_pos, self.board)

        reward = -1  # initialized with -1 to reduce no. of steps taken

        # Wrong action
        if self.harry_pos == old_harry_pos:
            reward -= 5

        # Cup distance reward
        new_d_to_cup = distance(self.harry_pos, self.cup_pos)

        # if harry moved closer to the cup or not
        if new_d_to_cup < old_d_to_cup:
            reward += 2 * (old_d_to_cup - new_d_to_cup)
        elif new_d_to_cup > old_d_to_cup:
            reward -= 1 * (new_d_to_cup - old_d_to_cup)

        # if harry moved away from death eater or not
        new_d_to_de = distance(self.harry_pos, self.death_eater_pos1)
        if new_d_to_de < old_d_to_de:
            reward -= 2 * (old_d_to_de - new_d_to_de)
        elif new_d_to_de > old_d_to_de:
            reward += 0.5 * (new_d_to_de - old_d_to_de)

        win = False
        done = False
        self.view_board = self.board.copy()
        self.view_board[self.harry_pos] = 2
        self.view_board[self.cup_pos] = 3
        self.view_board[self.death_eater_pos1] = 4
        self.view_board[self.death_eater_pos2] = 4

        if self.steps > 1000:
        # if max step limit exceeded
            reward -= 50
            done = True

        if self.harry_pos == self.death_eater_pos1 or self.harry_pos == self.death_eater_pos2:
        # Game Over
            reward = -100
            done = True

        elif self.harry_pos == self.cup_pos:
        # Game Won
            reward = 100
            done = True
            win = True

        # get state from position
        h_state = self.get_state(self.harry_pos)
        c_state = self.get_state(self.cup_pos)
        if old_d_to_de == old_d_to_de1:
            d_state = self.get_state(self.death_eater_pos1)
        else:
            d_state = self.get_state(self.death_eater_pos2)
        return (h_state, c_state, d_state), reward, done, win

# env = Env()
# env.reset()
# print(env.board[(0), 0])