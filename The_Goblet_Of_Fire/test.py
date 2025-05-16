import numpy as np
import matplotlib.pyplot as plt
from env import Env
import pygameview
# Parameters
Q_table = np.load("Q_table.npy")
env = Env()
n_states = len(env.zero_indices)
n_actions = 4
epochs = 100 # change to choose no. of generations
max_reward = 0

reward_arr = []
win_arr = []
frames = []
index = []
frames.append(np.ones_like(env.view_board))
frames.append(np.ones_like(env.view_board))
frames.append(np.ones_like(env.view_board))
frames.append(np.ones_like(env.view_board))
index.append('Start: The Triwizard Tournament')
index.append('Blue: Harry, Green: Cup, Red: Death Eater')
index.append('Blue: Harry, Green: Cup, Red: Death Eater')
index.append('Epoch 1')

# Q-learning
for epoch in range(epochs):
    env.reset()
    step = 0
    #print(f"Epoch {epoch+1}:")
    treward = 0
    h_state = env.h_state
    c_state = env.c_state
    d_state = env.d_state
    # print(h_state, c_state, d_state)
    while True:
        step+=1
        # print(env.view_board)
        frames.append(env.view_board)
        index.append(f'Step: {step}')
        # print(h_state, d_state)
        action = np.argmax(Q_table[h_state, c_state, d_state])
        # print(action)
        next_state, reward, done, win = env.step(int(action))
        treward += reward
        if env.steps > 100:
            # print("max step reached.")
            del frames[-100:] # if the max step limit reached implies, the episode is stuck, hence deleting frames
            win_arr.append(0)
            break

        h_state, c_state, d_state = next_state  # Update current state
        if done:
            reward_arr.append(treward)
            frames.append(np.ones_like(env.view_board))
            index.append(f'Episode {epoch+2}')
            if win:
                print(f"Epoch {epoch+1}: Win!")
                win_arr.append(1)
            else:
                print(f"Epoch {epoch+1}: Lost!")
                win_arr.append(0)
            break

print('win_rate: ', (sum(win_arr) / len(win_arr)))

# in graph 1 implies win, 0 implies game over
plt.title("Wins vs. Epochs")
plt.plot(win_arr)
plt.xlabel("episodes")
plt.ylabel("Win")
plt.savefig("./plots/test_wins.png")
plt.show()

pygameview.pygame_view(frames, index) # rendering the generations

# Print learned Q-table
# print("Learned Q-table:")
# print(Q_table)