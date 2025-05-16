import math
import numpy as np
import matplotlib.pyplot as plt
from env import Env
# Parameters

env = Env()
n_states = len(env.zero_indices)
n_actions = 4

Q_table = np.zeros(shape=(n_states, n_states, n_states,n_actions))
learning_rate = 0.8
discount_factor = 0.95
epsilon = 0.2
epochs = 100000

max_reward = 0

reward_arr = []
win_arr = []
success_rate = 0
avg_win_rate = 0

# Q-learning process
for epoch in range(epochs):
    env.reset()
    step = 0
    # print(f"Epoch {epoch+1}:")
    treward = 0
    h_state = env.h_state
    c_state = env.c_state
    d_state = env.d_state
    # print(h_state, c_state, d_state)
    epsilon = 0.8 * math.exp(-0.01 * epoch)
    while True:
        step+=1
        # print(env.view_board)
        # print(h_state, d_state)
        # Exploration vs. Exploitation (ϵ-greedy policy)
        # exploration_prob = min(1000 / (step * (treward + 1)), 1)
        if np.random.rand() < epsilon:
            action = np.random.randint(0, n_actions)
        else:
            action = np.argmax(Q_table[h_state, c_state, d_state])

        next_state, reward, done, win = env.step(int(action))
        treward += reward
        # print(epoch, treward, reward)
        # if treward > 200:
        #     print("epoch: ", epoch)
        # Q-value update rule (TD update)
        Q_table[h_state, c_state, d_state, action] += learning_rate * \
                                          (reward + discount_factor * np.max(Q_table[next_state]) - Q_table[
                                              h_state, c_state, d_state, action])

        h_state, c_state, d_state = next_state  # Update current state
        if env.steps > 1000:
            break
        if done:
            reward_arr.append(treward)
            if treward > max_reward:
                max_reward = treward
                # print(f"Epoch {epoch+1}: New best reward: {max_reward}")
            if win:
                # print(f"Epoch {epoch+1}: Win!")
                success_rate += 1
                avg_win_rate += 1

            else:
                # print(f"Epoch {epoch+1}: Lost!")
                if success_rate >= 10:
                    print(f"Episode: {epoch}, Win Streak: {success_rate}")
                success_rate = 0
            break
    if epoch % 10 == 0:
        win_arr.append(avg_win_rate / 10)
        avg_win_rate = 0

np.save("Q_table.npy", Q_table)
x_avg = []
y_avg = []
rang = 100
for ind in range(len(win_arr)-rang +1):
    y_avg.append(np.mean(win_arr[ind:ind+rang]))
    x_avg.append(ind+rang/2)


plt.title("Success Rate vs. Episodes")
plt.plot(win_arr, label="avg over 10 episodes")
plt.plot(x_avg, y_avg, color="red", linestyle='solid', linewidth=0.8, label="avg over 100 episodes")
plt.xlabel("episodes")
plt.ylabel("win rate (%)")
plt.legend(loc="upper left")
plt.savefig("./plots/success_rate.png")
plt.show()


x_avg = []
y_avg = []
rang = 100
for ind in range(len(reward_arr)-rang +1):
    y_avg.append(np.mean(reward_arr[ind:ind+rang]))
    x_avg.append(ind+rang/2)

plt.title("Average Reward vs. Episodes")
plt.plot(x_avg, y_avg, color="blue", linestyle='solid', linewidth=0.6, label="avg reward over 100 episodes")
plt.xlabel("episodes")
plt.ylabel("avg reward over 100 episodes")
plt.savefig("./plots/avg_reward.png")
plt.show()
# Print learned Q-table
# print("Learned Q-table:")
# print(Q_table)
