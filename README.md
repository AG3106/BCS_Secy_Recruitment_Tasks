# BCS_Secy_Recruitment_Tasks
Submissions for BCS Secretary Recruitment Tasks

### The Goblet of Fire:
**Instructions to run:** <br>
Training: Run `train.py` <br>
Run on pre-trained weights: Run `test.py`
<br><br>
**Environment:**<br>
The environment follows the instructions given, i.e, positions of harry, cup and death eater are randomly generated, death eater moves towards harry using BFS algorithm, etc.
<br><br>
**Reward Structure:**
1. At each step 1 was deducted from reward to reduce no. of steps taken.
2. If action led to no changes in position of harry (agent) then 5 was deducted.
3. Reward was given accordingly if harry moved closer/farther from cup.<br>
`reward += 2*(old_distance - new_distance)` if harry moved closer <br>
`reward -= 1*(new_distance - old_distance)` if harry moved farther <br>
*Note: Distance here is manhattan distance*
4. Reward was given in similar fashion if harry moved closer/farther from death eater.
5. If Game Over, i.e., death eater catches harry, the reward was set to be -100.
6. If Game Won, i.e., harry reaches the cup, the reward was set to be 100.


**Q-Learning Algorithm:**<br>
Since harry, cup, death eater can only be on empty blocks (not walls).
Hence, the possible states of game were `(no. of empty blocks)*3` each for harry, cup, death eater respectively.
<br>
Hence, for map used possible states of game were `(80, 80, 80)`
Hence, the shape of QTable was `(80, 80, 80, 4)`
<br>
Epsilon for epsilon greedy algorithm was chosen to be exponentially decaying.
This gave the agent the chance to explore initially and later to exploit and gather consecutive wins.
**Rendering:**
<br>
Pygame was used to render the game.
`view_board` from environment was saved for each step and later rendered in `pygameview.py`

**Evaluation:**
<br>
Training was done over 100000 episodes. The first 10 consecutive wins appear in between 30000-35000th episode.<br>
Plots of avg reward over episodes and success rate per 10 episodes were saved in `./plots`.
<br>
The trained weights were saved as `Q_table.npy`.
<br>
Testing was done over 100 episodes.
Winrate was about 90%. The plot of wins was saved in `./plots`.