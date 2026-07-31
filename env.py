import numpy as np
import random

class LineFollowerEnv:
    def __init__(self):
        self.grid_size = 30
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.dir_names = ['right', 'down', 'left', 'up']
        
        self.robot_pos = None
        self.robot_dir = None
        self.track = None
        self.line_path = []
        self.path_index = 0
        self.steps = 0
        self.max_steps = 150
        self.episode = 0
        
        self.difficulty_level = 1
        
    def get_difficulty_level(self, episode):
        if episode < 10000:
            return 1
        elif episode < 25000:
            return 2
        elif episode < 40000:
            return 3
        else:
            return 4
    
    def generate_track(self, difficulty):
        track = np.zeros((self.grid_size, self.grid_size), dtype=int)
        path = []
        
        if difficulty == 1:
            y = self.grid_size // 2
            for x in range(1, self.grid_size - 1):
                path.append((x, y))
        
        elif difficulty == 2:
            x, y = 1, self.grid_size // 2
            path.append((x, y))
            for i in range(1, 25):
                if i < 8:
                    x += 1
                elif i < 12:
                    y -= 1
                elif i < 20:
                    x += 1
                else:
                    y += 1
                if 1 <= x < self.grid_size - 1 and 1 <= y < self.grid_size - 1:
                    path.append((x, y))
        
        elif difficulty == 3:
            x, y = 1, self.grid_size // 2
            path.append((x, y))
            for i in range(1, 28):
                if i % 7 < 3:
                    x += 1
                elif i % 7 < 5:
                    y -= 1 if (i // 7) % 2 == 0 else -1
                else:
                    y += 1 if (i // 7) % 2 == 0 else 1
                if 1 <= x < self.grid_size - 1 and 1 <= y < self.grid_size - 1:
                    path.append((x, y))
        
        else:
            x, y = 1, self.grid_size // 2
            path.append((x, y))
            for i in range(1, 28):
                turn = random.choice([0, 0, 1, -1])
                if turn == 0:
                    x += 1
                elif turn == 1:
                    y += 1
                else:
                    y -= 1
                if 1 <= x < self.grid_size - 1 and 1 <= y < self.grid_size - 1:
                    path.append((x, y))
        
        for x, y in path:
            track[y, x] = 1
            if y > 0:
                track[y-1, x] = 2
            if y < self.grid_size - 1:
                track[y+1, x] = 2
            if x > 0:
                track[y, x-1] = 2
            if x < self.grid_size - 1:
                track[y, x+1] = 2
        
        return track, path
    
    def reset(self, episode=0):
        self.episode = episode
        self.difficulty_level = self.get_difficulty_level(episode)
        self.track, self.line_path = self.generate_track(self.difficulty_level)
        
        if len(self.line_path) > 0:
            self.robot_pos = self.line_path[0]
        else:
            self.robot_pos = (1, self.grid_size // 2)
        
        self.robot_dir = 0
        self.path_index = 0
        self.steps = 0
        
        return self.get_state()
    
    def get_sensor_reading(self):
        x, y = self.robot_pos
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return self.track[y, x]
        return 0
    
    def get_state(self):
        sensor_value = self.get_sensor_reading()
        if sensor_value == 0:
            return 0
        elif sensor_value == 1:
            return 1
        else:
            return 2
    
    def step(self, action):
        self.steps += 1
        
        if action == 0:
            self.robot_dir = (self.robot_dir - 1) % 4
        elif action == 2:
            self.robot_dir = (self.robot_dir + 1) % 4
        
        dx, dy = self.directions[self.robot_dir]
        new_x = self.robot_pos[0] + dx
        new_y = self.robot_pos[1] + dy
        
        if 0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size:
            self.robot_pos = (new_x, new_y)
        
        new_state = self.get_state()
        
        if new_state == 1:
            reward = 10
            self.path_index = min(self.path_index + 1, len(self.line_path) - 1)
        else:
            reward = -10
        
        if self.steps >= self.max_steps:
            reward += 100
            done = True
        elif self.robot_pos[0] >= self.grid_size - 2:
            reward += 200
            done = True
        else:
            done = False
        
        reward -= 0.1
        
        return new_state, reward, done, {'steps': self.steps, 'position': self.robot_pos}
    
    def get_track_info(self):
        return {
            'difficulty': self.difficulty_level,
            'track': self.track,
            'robot_pos': self.robot_pos,
            'robot_dir': self.robot_dir
        }
