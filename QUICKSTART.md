# Quick Start Guide

## For Simulation Training

1. **Install dependencies:**
   ```bash
   pip install numpy
   ```

2. **Run training:**
   ```bash
   python train_sim.py
   ```

3. **Check results:**
   - View `training_log.txt` for statistics
   - Q-table saved in `trained_qtable.json`

## For EV3 Robot Deployment

1. **Copy to EV3:**
   - `run_robot.py`
   - `trained_qtable.json`

2. **Verify sensor connections:**
   The program will automatically check sensors at startup. If you see an error, test manually:
   ```python
   # In run_robot.py, set:
   mode = "sensor"
   ```

3. **Adjust thresholds if needed:**
   ```python
   # In run_robot.py (for white line on black surface):
   WHITE_VALUE = 22  # Reading: white=31, edge=11 → midpoint 22
   BLACK_VALUE = 7   # Reading: black=3, edge=11 → midpoint 7
   ```

4. **Run line following:**
   ```python
   # In run_robot.py, set:
   mode = "run"
   ```

5. **Place robot on line** and start the program!

**IMPORTANT:** Position the robot with the color sensor on the **edge** of the white line (not fully on white or black). If "Config error" appears, the robot will search for the line edge automatically up to 5 times.

## For EV3 Fine-tuning

To continue learning on the actual robot:

```python
# In run_robot.py, set:
mode = "finetune"
```

- Loads the existing `trained_qtable.json`
- Shows `Episode X/5000` on the EV3 screen
- Saves the Q-table after **every** episode (progress is never lost if you stop)
- An episode ends when accumulated reward exceeds 300

## Common Issues

**Sensor verification failed at startup:**
- The program automatically checks sensors before running
- If you see "Sensor verification failed", check:
  - Color sensor connected to Port S1
  - IR sensor connected to Port S4
  - All cables are fully seated
- Run with `mode = "sensor"` to test manually

**OSError: [Errno 19] ENODEV - Sensor not connected:**
- Check that sensors are connected to correct ports:
  - Color sensor: Port S1
  - IR sensor: Port S4
- Check cable connections are fully seated
- Run sensor test mode first: `mode = "sensor"`

**Robot spinning or going off track:**
- Check motor ports (D and A)
- Test with `mode = "sensor"` first

**Not detecting line:**
- Adjust `WHITE_VALUE` and `BLACK_VALUE`
- Ensure good lighting conditions
- Check sensor is facing the surface

**Hitting obstacles:**
- Verify IR sensor connection (Port **S4**)
- Adjust `DISTANCE_TO_OBSTACLE` threshold

**Config error:**
- Position robot with sensor on the **edge** of the line (reading ~11)
- Robot auto-searches (turns 90°) up to 5 times before giving up
- Check debug output: `Left scan`, `Right scan`, `Config pattern`

**Q-table won't load (UnicodeError):**
- Use `trained_qtable.json`, not a `.pkl` file
- Regenerate with `python train_sim.py` if missing or corrupted

## File Descriptions

- `env.py` - Simulation environment (used for training)
- `agent.py` - Q-learning agent (used for training)
- `train_sim.py` - Training script (run this to train)
- `run_robot.py` - EV3 robot code (copy this to EV3)
- `trained_qtable.json` - Trained Q-table in JSON format (copy this to EV3)

## Need Help?

See `README.md` for detailed documentation.
