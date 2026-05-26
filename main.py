import gymnasium
import random
import torch 
import torch.nn as nn


#constants
NUMBER_OF_EPISODES = 20000
DEBUG = True


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
    
lrate = 0.001
model = NeuralNetwork()
#ready loss and backpropagating functions
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lrate)


'''
UNDERSTANDING INPUT AND OUTPUT DEBUGGING
obs, info = env.reset()
print(obs)
obs_tensor = torch.tensor(obs)
q_val = model(obs_tensor)
print(q_val)
action = torch.argmax(q_val).item()
print("action: ", action)
'''

#decides action for agent, either random or NN based.
#takes tensor and int as inputs, returns integer (action code)
def epsilon_greedy_action(x, epsilon):
    chance = random.random()

    if chance < epsilon:
        action = random.randint(0,3)        #random choice
        if DEBUG:
            print("Random action selected: ", action)
    else:
        with torch.no_grad():               
            qvalues = model(x)
            action = torch.argmax(qvalues).item()
        if DEBUG:
            print("Model determined: qValues: ", qvalues, " action: ", action)

    return action

#main loop of training in the enviroment
def training():
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

    env.close()  



''' TESTING ZONE '''

obs, info = env.reset()     #starting state
obs_tensor = torch.tensor(obs)

#three random actions
epsilon_greedy_action(obs_tensor, 1)
epsilon_greedy_action(obs_tensor, 1)
epsilon_greedy_action(obs_tensor, 1)
#three NN actions
epsilon_greedy_action(obs_tensor, 0)
epsilon_greedy_action(obs_tensor, 0)
epsilon_greedy_action(obs_tensor, 0)