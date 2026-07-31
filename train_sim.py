from env import LineFollowerEnv
from agent import QLearningAgent
import time

def train(episodes=50000, alpha=0.2, gamma=0.9, initial_epsilon=1.0, final_epsilon=0.01):
    env = LineFollowerEnv()
    agent = QLearningAgent(num_states=3, num_actions=3, alpha=alpha, gamma=gamma)
    
    epsilon_decay = (initial_epsilon - final_epsilon) / episodes
    
    epsilon = initial_epsilon
    
    total_rewards = []
    episode_lengths = []
    success_count = 0
    
    print("=" * 70)
    print("Q-LEARNING LINE FOLLOWER - SIMULATION TRAINING")
    print("=" * 70)
    print(f"Total Episodes: {episodes}")
    print(f"Learning Rate (Alpha): {alpha}")
    print(f"Discount Factor (Gamma): {gamma}")
    print(f"Initial Epsilon: {initial_epsilon}")
    print(f"Final Epsilon: {final_epsilon}")
    print("=" * 70)
    print()
    
    start_time = time.time()
    
    for episode in range(episodes):
        state = env.reset(episode)
        total_reward = 0
        steps = 0
        done = False
        
        while not done:
            action = agent.choose_action(state, epsilon)
            next_state, reward, done, info = env.step(action)
            
            agent.update_q_value(state, action, reward, next_state)
            
            state = next_state
            total_reward += reward
            steps += 1
        
        total_rewards.append(total_reward)
        episode_lengths.append(steps)
        
        if total_reward > 300:
            success_count += 1
        
        if (episode + 1) % 1000 == 0:
            avg_reward = sum(total_rewards[-1000:]) / 1000
            avg_steps = sum(episode_lengths[-1000:]) / 1000
            success_rate = (success_count / 1000) * 100
            
            elapsed_time = time.time() - start_time
            
            print(f"Episode {episode + 1:6d} | "
                  f"Avg Reward: {avg_reward:6.2f} | "
                  f"Avg Steps: {avg_steps:5.1f} | "
                  f"Success: {success_rate:5.1f}% | "
                  f"Epsilon: {epsilon:.3f} | "
                  f"Difficulty: {env.difficulty_level} | "
                  f"Time: {elapsed_time:.1f}s")
            
            success_count = 0
        
        epsilon = max(final_epsilon, epsilon - epsilon_decay)
    
    total_time = time.time() - start_time
    
    print()
    print("=" * 70)
    print("TRAINING COMPLETED")
    print("=" * 70)
    print(f"Total Time: {total_time:.2f} seconds")
    print(f"Average Time per Episode: {total_time/episodes:.4f} seconds")
    print(f"Final Epsilon: {epsilon:.4f}")
    print()
    
    agent.print_q_table()
    
    agent.save_q_table('trained_qtable.json')
    
    with open('training_log.txt', 'w') as f:
        f.write("Q-Learning Line Follower - Training Log\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Total Episodes: {episodes}\n")
        f.write(f"Learning Rate (Alpha): {alpha}\n")
        f.write(f"Discount Factor (Gamma): {gamma}\n")
        f.write(f"Initial Epsilon: {initial_epsilon}\n")
        f.write(f"Final Epsilon: {final_epsilon}\n")
        f.write(f"Total Training Time: {total_time:.2f} seconds\n\n")
        
        f.write("Final Q-Table:\n")
        f.write("State\\Action | Left | Forward | Right\n")
        f.write("-" * 40 + "\n")
        state_names = ['Black', 'Margin', 'White']
        for i in range(3):
            f.write(f"{state_names[i]:11} | {agent.q_table[i, 0]:5.2f} | {agent.q_table[i, 1]:7.2f} | {agent.q_table[i, 2]:5.2f}\n")
        f.write("\n")
        
        f.write("Training Statistics (Last 1000 Episodes):\n")
        f.write(f"Average Reward: {sum(total_rewards[-1000:])/1000:.2f}\n")
        f.write(f"Average Steps: {sum(episode_lengths[-1000:])/1000:.2f}\n")
        f.write(f"Min Reward: {min(total_rewards[-1000:]):.2f}\n")
        f.write(f"Max Reward: {max(total_rewards[-1000:]):.2f}\n")
    
    print("Training log saved to 'training_log.txt'")
    print()
    
    return agent

if __name__ == "__main__":
    agent = train(episodes=50000, alpha=0.2, gamma=0.9)
