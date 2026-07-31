import numpy as np
import json
import random

class QLearningAgent:
    def __init__(self, num_states=3, num_actions=3, alpha=0.2, gamma=0.9):
        self.num_states = num_states
        self.num_actions = num_actions
        self.alpha = alpha
        self.gamma = gamma
        
        self.q_table = np.zeros((num_states, num_actions))
        
    def choose_action(self, state, epsilon):
        if random.random() < epsilon:
            return random.randint(0, self.num_actions - 1)
        else:
            return np.argmax(self.q_table[state])
    
    def update_q_value(self, state, action, reward, next_state):
        max_next_q = np.max(self.q_table[next_state])
        current_q = self.q_table[state, action]
        
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state, action] = new_q
        
        return new_q - current_q
    
    def save_q_table(self, filename='trained_qtable.json'):
        with open(filename, 'w') as f:
            json.dump(self.q_table.tolist(), f, indent=2)
        print("Q-table saved to", filename)
    
    def load_q_table(self, filename='trained_qtable.json'):
        with open(filename, 'r') as f:
            self.q_table = np.array(json.load(f))
        print("Q-table loaded from", filename)
    
    def print_q_table(self):
        print("\nQ-Table:")
        print("State\\Action | Left | Forward | Right")
        print("-" * 40)
        for i in range(self.num_states):
            state_name = ['Black', 'Margin', 'White'][i]
            print(f"{state_name:11} | {self.q_table[i, 0]:5.2f} | {self.q_table[i, 1]:7.2f} | {self.q_table[i, 2]:5.2f}")
        print()
    
    def get_best_action(self, state):
        return np.argmax(self.q_table[state])
    
    def get_q_values(self, state):
        return self.q_table[state]
