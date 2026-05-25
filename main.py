import gymnasium
import random
import torch 
import torch.nn as nn


#constants
NUMBER_OF_EPISODES = 20000


#hyperparameters of Q learning
ALPHA = 0.1         #learning rate
GAMMA = 0.99        #"importance of future"
INITIAL_EPSILON = 0.999       #random move probability
MINIMAL_EPSILON = 0.1
Q = {}


env = gymnasium.make("LunarLander-v3", continuous=False, gravity=-10.0,
               enable_wind=False, wind_power=15.0, turbulence_power=0.5)

class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.first = nn.Linear(8,64)
        self.ReLU = nn.ReLU()
        self.second = nn.Linear(64, 64)
        self.last = nn.Linear(64, 4)
    
    def forward(self, x):
        x = self.first(x)
        x = self.ReLU(x)
        x = self.second(x)
        x = self.ReLU(x)
        x = self.last(x)
        return x
    
model = NeuralNetwork()

obs, info = env.reset()

print(obs)

obs_tensor = torch.tensor(obs)
q_val = model(obs_tensor)
print(q_val)
action = torch.argmax(q_val).item()
print("action: ", action)


'''       
for episode in range(NUMBER_OF_EPISODES):
    obs, info = env.reset()     #starting state
    episode_ended = False
    total_reward = 0
    steps = 0
    epsilon = max((epsilon * 0.999), MINIMAL_EPSILON)

    while not done:

        action = random.randint(0,3)
        
        next_obs, reward, terminated, truncated, info = env.step(action)    #take the next step
        done = terminated or truncated                                      #check if crashed or truncuated

        
        obs = next_obs                                                          #next step becomes initial step

    
        total_reward += reward                                                  #sum rewards
        steps += 1                                                              #sum steps
'''
env.close()  
