#!/usr/bin/env pybricks-micropython
import random
import json
import time
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (
    Motor,
    TouchSensor,
    ColorSensor,
    InfraredSensor,
    UltrasonicSensor,
    GyroSensor,
)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

ev3 = EV3Brick()

LEFT_MOTOR = Port.D
RIGHT_MOTOR = Port.A
LIGHT_SENSOR = Port.S1
OBSTACLE_SENSOR = Port.S4

WHITE_VALUE = 22
BLACK_VALUE = 7
TURN_ANGLE = 5
DRIVE_SPEED = 10
WHEEL_DIAMETER = 56
AXLE_TRACK = 110
DISTANCE_TO_OBSTACLE = 25

ALPHA = 0.2
GAMMA = 0.9
FINETUNE_EPSILON = 0.05

STATES = ["black", "margin", "white"]
ACTIONS = ["left", "forward", "right"]

CONFIG_0 = [(0, 2, 1), (2, 0, 1), (1, 2, 2), (1, 0, 0)]
CONFIG_1 = [(2, 2, 1), (0, 0, 1), (1, 2, 0), (1, 0, 2)]

leftMotor = Motor(LEFT_MOTOR)
rightMotor = Motor(RIGHT_MOTOR)
lightSensor = ColorSensor(LIGHT_SENSOR)
obstacleSensor = InfraredSensor(OBSTACLE_SENSOR)

suppressed = False
config = None
QTable = None
filePath = "trained_qtable.json"

robot = DriveBase(leftMotor, rightMotor, WHEEL_DIAMETER, AXLE_TRACK)


def loadQTable():
    print("Loading Q Table")
    with open(filePath, "r") as file:
        loadedData = json.load(file)
    return loadedData


def printQTable():
    print("Q-Table:")
    print("State\\Action | Left | Forward | Right")
    print("-" * 40)
    for i, row in enumerate(QTable):
        print(STATES[i], "|", row[0], "|", row[1], "|", row[2])
    print()


def getState():
    sr = lightSensor.reflection()
    if sr < BLACK_VALUE:
        return 0
    elif sr >= BLACK_VALUE and sr <= WHITE_VALUE:
        return 1
    elif sr > WHITE_VALUE:
        return 2


def moveForward(speed):
    robot.straight(speed)


def moveBackward(speed):
    robot.straight(-speed)


def turnRight(angle):
    robot.turn(angle)


def turnLeft(angle):
    robot.turn(-angle)


def getConfig():
    turnLeft(40)
    l = getState()
    print("Left scan: state", l)
    turnRight(80)
    r = getState()
    print("Right scan: state", r)
    turnLeft(40)

    print("Config pattern: (", l, ",", r, ")")

    if (l, r) == (0, 2):
        print("Config: 0")
        return 0
    elif (l, r) == (2, 0):
        print("Config: 1")
        return 1
    elif l in [0, 1] and r in [1, 2]:
        print("Config: 0 (margin tolerated)")
        return 0
    elif l in [1, 2] and r in [0, 1]:
        print("Config: 1 (margin tolerated)")
        return 1
    else:
        print("ERROR: Pattern not recognized")
        return None


def configProof(action, config):
    if action == 1:
        return action
    elif config == 0:
        return action
    elif config == 1:
        if action == 0:
            return 2
        elif action == 2:
            return 0


def obstacleAvailable():
    obstacleStatus = obstacleSensor.distance() < DISTANCE_TO_OBSTACLE
    if obstacleStatus:
        print("Obstacle detected")
    return obstacleStatus


def executeActionTest(action):
    if action == 0:
        robot.drive(0, -80)
    elif action == 1:
        robot.drive(300, 0)
    elif action == 2:
        robot.drive(0, 80)


def updateQTable(prevState, newState, action, reward, config):
    action = configProof(action, config)
    maxNextQ = max(QTable[newState])
    tableUpdate = ALPHA * (reward + GAMMA * maxNextQ - QTable[prevState][action])
    QTable[prevState][action] += tableUpdate
    return tableUpdate


def executeActionLearn(action, state):
    count = 1
    if action == 0:
        while getState() == state:
            turnLeft(TURN_ANGLE)
            count += 1
    elif action == 1:
        moveForward(DRIVE_SPEED)
        count += 1
    elif action == 2:
        while getState() == state:
            turnRight(TURN_ANGLE)
            count += 1

    newState = getState()

    if newState == 0 or newState == 2:
        reward = -10
    elif newState == 1:
        reward = 60 / count

    return newState, reward


def pickAction(state, epsilon, config):
    if random.random() < epsilon:
        action = random.randint(0, 2)
        print("random: ", end="")
        return action
    else:
        action = configProof(QTable[state].index(max(QTable[state])), config)
        print("table: ", end="")
        return action


def finetune(episodes=100):
    global QTable
    global config

    print("Starting fine-tuning on EV3...")
    ev3.speaker.beep(500, 500)

    QTable = loadQTable()
    printQTable()

    config = getConfig()
    if config is None:
        print("Config error")
        return

    epsilon = FINETUNE_EPSILON

    for episode in range(episodes):
        print("Fine-tune Episode", episode + 1)

        ev3.screen.clear()
        ev3.screen.draw_text(10, 30, "Fine-tuning")
        ev3.screen.draw_text(
            10, 55, "Episode " + str(episode + 1) + "/" + str(episodes)
        )

        state = getState()
        totalReward = 0

        while totalReward <= 300:
            action = pickAction(state, epsilon, config)
            newState, reward = executeActionLearn(action, state)

            print(
                STATES[state],
                "->",
                ACTIONS[action],
                "->",
                STATES[newState],
                ": Reward",
                reward,
            )

            updateQTable(state, newState, action, reward, config)

            transition = (state, action, newState)
            if transition in CONFIG_0:
                config = 0
            elif transition in CONFIG_1:
                config = 1

            state = newState
            totalReward += reward
            print("Total Reward:", totalReward)

        epsilon = max(0.01, epsilon * 0.95)

        with open(filePath, "w") as f:
            json.dump(QTable, f, indent=2)
        print("Episode", episode + 1, "saved")

    ev3.speaker.beep(1000, 500)


def lineFollowingBehavior():
    print("Line following")
    global config
    global suppressed

    while not suppressed:
        state = getState()
        action = configProof(QTable[state].index(max(QTable[state])), config)
        executeActionTest(action)

        if obstacleAvailable():
            suppressed = True


def obstacleAvoidanceBehavior():
    ev3.speaker.beep(700, 300)
    print("Obstacle avoiding")
    global config
    global suppressed

    while True:
        robot.stop()
        moveBackward(100)
        turnRight(360)

        config = 0 if config == 1 else 1

        if not obstacleAvailable():
            suppressed = False
            break

    ev3.speaker.beep(700, 300)


def run():
    global QTable
    global config

    QTable = loadQTable()
    printQTable()

    attempts = 0
    config = getConfig()
    while config is None and attempts < 5:
        attempts += 1
        print("Config detection failed. Attempt", attempts, "of 5")
        print("Searching for line edge...")
        robot.stop()
        robot.turn(90)
        config = getConfig()

    if config is None:
        print("Config error after 5 attempts")
        print("Please position robot with sensor on the line edge and restart")
        return

    ev3.speaker.beep(500, 500)
    print("Starting line following...")

    while True:
        if obstacleAvailable():
            obstacleAvoidanceBehavior()
        else:
            lineFollowingBehavior()


def verifySensors():
    print("Verifying sensor connections...")
    try:
        lightIntensity = lightSensor.reflection()
        print("Light Sensor (Port.S1): OK - Reading:", lightIntensity)
    except Exception as e:
        print("Light Sensor (Port.S1): FAILED -", str(e))
        return False

    try:
        irDistance = obstacleSensor.distance()
        print("IR Sensor (Port.S4): OK - Distance:", irDistance, "mm")
    except Exception as e:
        print("IR Sensor (Port.S4): FAILED -", str(e))
        return False

    print("All sensors verified successfully!")
    return True


def sensorRead():
    ev3.speaker.beep(500, 500)
    print("Sensor Test Mode")
    print("Light Sensor: Port.S1")
    print("IR Sensor: Port.S4")
    print("Press ENTER to stop")
    print("-" * 40)
    while True:
        lightIntensity = lightSensor.reflection()
        irDistance = obstacleSensor.distance()
        print("Light:", lightIntensity, "| IR Distance:", irDistance, "mm")
        ev3.screen.draw_text(0, 0, "Light: " + str(lightIntensity))
        ev3.screen.draw_text(0, 20, "IR: " + str(irDistance) + "mm")
        time.sleep(0.5)
        ev3.screen.clear()


if __name__ == "__main__":
    mode = "run"

    if not verifySensors():
        print("Sensor verification failed! Check connections.")
        print("Try mode = 'sensor' to test sensors manually.")
        exit(1)

    if mode == "run":
        run()
    elif mode == "finetune":
        finetune(episodes=5000)
        run()
    elif mode == "sensor":
        sensorRead()
