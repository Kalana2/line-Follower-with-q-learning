# Q-Learning Line Follower for EV3 Robot

A reinforcement learning-based line following system for LEGO EV3 robot using Q-learning algorithm. The system includes a simulation environment for training and deployment code for the actual EV3 robot.

## Overview

This project implements a Q-learning agent that learns to follow a white line on a black surface through simulation training. The trained Q-table is then deployed to an actual EV3 robot for real-world line following.

### Key Features

- **Simulation-based Training**: Train the agent in a simulated environment before deploying to hardware
- **Progressive Difficulty**: Training progresses through 4 difficulty levels (straight lines → curves → complex tracks)
- **50,000 Episodes**: Extensive training for robust Q-table learning
- **Real-time Deployment**: Pre-trained Q-table for immediate EV3 deployment
- **Optional Fine-tuning**: Continue learning on the actual robot if needed
- **Obstacle Avoidance**: Built-in obstacle detection and avoidance
- **MicroPython v1.11 Compatible**: No f-strings or advanced formatting — runs on older EV3 MicroPython
- **Automatic Sensor Verification**: Checks all sensors at startup before running
- **Per-Episode Saving**: Q-table is saved after every fine-tuning episode, never lost on stop
- **On-Screen Episode Display**: EV3 screen shows current episode during fine-tuning

## Project Structure

```
Assignment 2/
├── env.py                    # Simulation environment
├── agent.py                  # Q-learning agent
├── train_sim.py              # Training script
├── run_robot.py              # EV3 robot control code
├── trained_qtable.json       # Pre-trained Q-table (generated)
├── training_log.txt          # Training statistics (generated)
└── README.md                 # This file
```

## How It Works

### Q-Learning Algorithm

The system uses Q-learning, a model-free reinforcement learning algorithm:

- **States**: 3 states based on color sensor readings
  - State 0 (Black): Sensor reading < 7 (off track)
  - State 1 (Margin): 7 ≤ reading ≤ 22 (on line edge)
  - State 2 (White): reading > 22 (center of line)

  Thresholds are calibrated for a white line on a black surface with measured
  readings of black=3, edge=11, white=31. Adjust `BLACK_VALUE` and
  `WHITE_VALUE` in `run_robot.py` if your surface differs.

- **Actions**: 3 possible actions
  - Action 0: Turn left
  - Action 1: Move forward
  - Action 2: Turn right

- **Reward Structure**:
  - On margin (correct position): +10
  - Off track (black/white): -10
  - Episode completion bonus: +100
  - Step penalty: -0.1 (encourages efficiency)

### Training Process

1. **Progressive Difficulty**:
   - Episodes 0-10,000: Simple straight lines (Level 1)
   - Episodes 10,001-25,000: Gentle curves (Level 2)
   - Episodes 25,001-40,000: Sharp turns (Level 3)
   - Episodes 40,001-50,000: Complex tracks (Level 4)

2. **Exploration-Exploitation**:
   - Epsilon starts at 1.0 (pure exploration)
   - Decays to 0.01 (mostly exploitation)
   - Allows learning then applying learned policy

3. **Q-Table Updates**:
   - Uses Bellman equation: Q(s,a) = Q(s,a) + α[r + γ·max(Q(s',a')) - Q(s,a)]
   - Learning rate (α): 0.2
   - Discount factor (γ): 0.9

## Installation

### Requirements

**For Simulation Training:**
- Python 3.6+
- NumPy

Install dependencies:
```bash
pip install numpy
```

**For EV3 Robot:**
- LEGO EV3 brick with ev3dev operating system
- Pybricks MicroPython v2.0 or higher
- Hardware setup:
  - Left motor: Port D
  - Right motor: Port A
  - Color sensor (light sensor): Port S1
  - Infrared sensor (obstacle detection): Port S4

## Usage

### 1. Running Simulation Training

To train the Q-learning agent from scratch:

```bash
python train_sim.py
```

This will:
- Run 50,000 episodes of training
- Display progress every 1,000 episodes
- Save the trained Q-table to `trained_qtable.json`
- Generate training statistics in `training_log.txt`

**Expected output:**
```
======================================================================
Q-LEARNING LINE FOLLOWER - SIMULATION TRAINING
======================================================================
Total Episodes: 50000
Learning Rate (Alpha): 0.2
Discount Factor (Gamma): 0.9
Initial Epsilon: 1.0
Final Epsilon: 0.01
======================================================================

Episode   1000 | Avg Reward: -907.18 | Avg Steps: 100.0 | Success:   0.0% | Epsilon: 0.980 | Difficulty: 1 | Time: 0.5s
...
Episode  50000 | Avg Reward: -1248.68 | Avg Steps: 136.5 | Success:  0.0% | Epsilon: 0.010 | Difficulty: 4 | Time: 70.6s

======================================================================
TRAINING COMPLETED
======================================================================
```

### 2. Deploying to EV3 Robot

**Step 1: Transfer files to EV3**
Copy these files to your EV3 robot:
- `run_robot.py`
- `trained_qtable.json`

**Step 2: Configure robot ports**
Edit `run_robot.py` if your port configuration differs:
```python
LEFT_MOTOR = Port.D
RIGHT_MOTOR = Port.A
LIGHT_SENSOR = Port.S1
OBSTACLE_SENSOR = Port.S4
```

**Step 3: Set sensor thresholds**
Adjust based on your actual sensor readings (test with `mode = "sensor"` first):
```python
WHITE_VALUE = 22  # Midpoint between edge (11) and white (31)
BLACK_VALUE = 7   # Midpoint between black (3) and edge (11)
```

**Step 4: Choose operating mode**
Edit the `mode` variable in `run_robot.py`:
```python
mode = "run"       # Normal line following with pre-trained Q-table
mode = "finetune"  # Fine-tune on robot, then run
mode = "sensor"    # Test sensor readings only
```

**Step 5: Run the program**
Execute on EV3 using Pybricks or ev3dev.

The program will automatically verify sensor connections at startup. If any sensor is not detected, it will display an error message and exit. Use `mode = "sensor"` to test sensors manually if needed.

### 3. Fine-tuning on EV3

If you want to improve the Q-table with real-world experience:

```python
mode = "finetune"
```

This will:
- Load the existing `trained_qtable.json` (continues from current values)
- Run fine-tuning episodes on the actual robot (default: 5,000)
- Display the current episode on the EV3 screen (`Episode X/5000`)
- Save the Q-table to `trained_qtable.json` **after every episode**
- Then start line following automatically

**How an episode is measured:** An episode ends when the accumulated reward
exceeds 300. Rewards come from `executeActionLearn()`: landing on the margin
(state 1) gives up to `+60`, landing off the line (state 0 or 2) gives `-10`.
So an episode ≈ successfully following the line for several transitions.

**Saving behavior:** The Q-table is written to disk after each episode finishes.
If you stop the program at any point, all completed episodes are preserved —
nothing is lost. Epsilon starts at `FINETUNE_EPSILON` (0.05) and decays by
×0.95 each episode (minimum 0.01).

## Configuration

### Training Parameters

Edit `train_sim.py` to customize training:

```python
def train(episodes=50000, alpha=0.2, gamma=0.9, 
          initial_epsilon=1.0, final_epsilon=0.01):
```

- `episodes`: Number of training episodes (default: 50,000)
- `alpha`: Learning rate (default: 0.2)
- `gamma`: Discount factor (default: 0.9)
- `initial_epsilon`: Starting exploration rate (default: 1.0)
- `final_epsilon`: Ending exploration rate (default: 0.01)

### Robot Parameters

Edit `run_robot.py` to customize robot behavior:

```python
WHITE_VALUE = 22          # White line sensor threshold
BLACK_VALUE = 7           # Black surface sensor threshold
TURN_ANGLE = 5            # Turn angle in degrees
DRIVE_SPEED = 10          # Forward speed
DISTANCE_TO_OBSTACLE = 25 # Obstacle detection distance (mm)
```

**Sensor thresholds:** For a white line on a black surface with readings of black=3, edge=11, white=31, use `BLACK_VALUE = 7` and `WHITE_VALUE = 22`. These are the midpoints between adjacent readings.

## Understanding the Q-Table

The Q-table is a 3×3 matrix representing learned values for each state-action pair:

```
State\Action | Left    | Forward | Right
----------------------------------------
Black        | -97.82  | -77.83  | -97.79
Margin       | -89.10  | -86.64  | -89.00
White        | -91.83  | -97.77  | -97.74
```

**Interpretation:**
- **Black state**: Forward has highest value (-77.83) → robot moves forward to find the line
- **Margin state**: Forward has highest value (-86.64) → robot continues forward on the line
- **White state**: Right has highest value (-97.74) → robot turns right to get back to margin

Higher Q-values indicate better actions. The robot always chooses the action with the highest Q-value for the current state.

### Q-Table File Format (JSON)

The Q-table is stored as a JSON file (`trained_qtable.json`), a plain-text
format that is compatible with both desktop Python and MicroPython (unlike
`pickle`, which caused `UnicodeError` on the EV3). The file is a 3×3 list:

```json
[
  [-97.82, -77.83, -97.79],
  [-89.10, -86.64, -89.00],
  [-91.83, -97.77, -97.74]
]
```

The first index is the state (0=black, 1=margin, 2=white); the second index
is the action (0=left, 1=forward, 2=right).

## MicroPython v1.11 Compatibility

The EV3 in this project runs **Pybricks MicroPython v1.11**, which does **not**
support:

- **f-strings** (`f"..."`) → `SyntaxError: invalid syntax`
- **`.format()` with format specifiers** (e.g., `"{:.2f}".format(...)`)
- **`str.capitalize()`** in some contexts

`run_robot.py` therefore uses only basic, universally supported constructs:

```python
# Instead of:  print(f"{name:11} | {row[0]:5.2f} | ...")
print(STATES[i], "|", row[0], "|", row[1], "|", row[2])

# Instead of:  print("Episode {}".format(episode + 1))
print("Episode", episode + 1)
```

**Rule of thumb:** when editing `run_robot.py`, use plain `print(...)` with
comma-separated values and string concatenation with `+` and `str()`.

## Config Detection

Before following the line, the robot determines its orientation relative to
the line using `getConfig()`. It turns left 40°, reads the state, turns right
80°, reads the state, then turns back:

- **Config 0**: left scan sees black (0), right scan sees white (2)
- **Config 1**: left scan sees white (2), right scan sees black (0)

The function also accepts margin states (1) to be tolerant of imperfect
positioning, and prints debug output (`Left scan`, `Right scan`,
`Config pattern`) to help diagnose issues.

If config detection fails, `run()` automatically **retries up to 5 times**,
turning 90° between attempts to search for the line edge. If it still fails,
the robot stops and asks you to position it manually.

## Troubleshooting

### Robot not following line properly

1. **Check sensor thresholds**: Run sensor test mode
   ```python
   mode = "sensor"
   ```
   Adjust `WHITE_VALUE` and `BLACK_VALUE` based on actual readings

2. **Position robot on line edge**: The robot must start with the sensor
   exactly on the edge of the line (reading around 11 for a white line on
   black surface). If the sensor is fully on white or black, `getConfig()`
   will fail.

3. **Verify motor directions**: Ensure motors are connected to correct ports

4. **Check initial configuration**: Robot must start on the line edge.
   If "Config error" appears, the robot will automatically search for the
   line edge up to 5 times before stopping.

### Training not converging

1. **Increase episodes**: Try 100,000 episodes
2. **Adjust learning rate**: Try alpha = 0.3
3. **Modify reward structure**: Increase positive rewards

### Obstacle detection issues

1. **Check IR sensor**: Ensure obstacle sensor is connected to Port **S4**
2. **Adjust distance threshold**: Modify `DISTANCE_TO_OBSTACLE`

### Sensor verification failed (OSError: [Errno 19] ENODEV)

The program verifies all sensors at startup. If verification fails with
`ENODEV`, a sensor is not detected on its expected port:

- Color (light) sensor must be on Port **S1**
- IR sensor must be on Port **S4**
- Check that cables are fully seated
- Use `mode = "sensor"` to test readings manually

### Config error

If `getConfig()` cannot recognize a valid orientation pattern, the robot
retries (turning 90°) up to 5 times. To fix:

1. Place the robot with the sensor **on the edge** of the line (reading ~11),
   not fully on white or black
2. Verify thresholds match your surface (`BLACK_VALUE`, `WHITE_VALUE`)
3. Check the debug output (`Left scan`, `Right scan`, `Config pattern`) to
   see what states are detected

### Q-table not loading (UnicodeError / file errors)

The Q-table must be the JSON file `trained_qtable.json`, **not** a pickle
file. MicroPython cannot load `pickle` files created by desktop Python.
Re-generate with `python train_sim.py` if the file is missing or corrupted.

## Performance Metrics

After 50,000 episodes of training:

- **Training Time**: ~70 seconds
- **Final Average Reward**: -1248.68
- **Final Average Steps**: 136.5
- **Q-Table Size**: 3×3 (9 values)

## References

- Original reference implementation: `q-learning-line-follower-for-ev3-main/`
- Q-learning algorithm: Sutton & Barto, "Reinforcement Learning: An Introduction"
- EV3 MicroPython documentation: https://pybricks.com/

## License

This project is created for educational purposes as part of SCS3305-IS3212 Robotics and Cognitive Systems course.

## Author

Created for EV3 Robot Q-Learning Line Follower Project
