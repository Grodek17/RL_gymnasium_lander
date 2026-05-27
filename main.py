import gymnasium
import random
import torch 
import torch.nn as nn


#constants
NUMBER_OF_EPISODES = 20
BUFFER_SIZE = 100
DEBUG = True


#hyperparameters of Q learning
ALPHA = 0.1         #learning rate
GAMMA = 0.99        #"importance of future"
INITIAL_EPSILON = 0.999       #random move probability
MINIMAL_EPSILON = 0.1
Q = {}

''' CLASSES '''
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
    
#class for storing states of the enviroment, for training the neural network
class ExperienceBuffer():
    def __init__(self, max_size):
        self.buffersize = max_size
        self.buffer = []

    #arguments passed as tensors
    def add(self, observation, action, next_observation, reward, done):
        if(len(self.buffer) > self.buffersize):
            if DEBUG:
                print("List approached full capacity, removing oldest record")
            self.buffer.pop(0)
        
        self.buffer.append((observation, action, next_observation, reward, done))

    def giveRandomBatch(self, batch_size):
        if DEBUG:
            print("selecting batch_size random entries from list")

        if len(self.buffer) < (self.buffersize - 1):
            raise ValueError("Buffer not full, cannot give random batch")

        batch = []
        for x in range(batch_size):
            index = random.randint(0, self.buffersize - 1)
            batch.append(self.buffer[index])
            print("DEBUG: selected index: ", index, " batch: ", batch)
        
        if DEBUG:
            print("whole buffer: ", self.buffer)
            print("selected random batch: ", batch, "batch size: ", len(batch))
        
        return batch

    
    def printBuffer(self):
        print("=== PRINT STARTED ===")
        for x in range(len(self.buffer)):
            print(x, ": ", self.buffer[x])


lrate = 0.001
model = NeuralNetwork()
buffer = ExperienceBuffer(20)
#ready loss and backpropagating functions
loss_fn = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=lrate)

env = gymnasium.make("LunarLander-v3", continuous=False, gravity=-10.0,
               enable_wind=False, wind_power=15.0, turbulence_power=0.5)






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

def modelLearning():
    pass
#main loop of training in the enviroment
def training():
    epsilon = INITIAL_EPSILON
    for episode in range(NUMBER_OF_EPISODES):
        obs, info = env.reset()             #starting state
        episode_ended = False
        total_reward = 0
        steps = 0
        epsilon = max((epsilon * 0.999), MINIMAL_EPSILON)

        while not episode_ended:
            obs_tensor = torch.tensor(obs)      #turning observation into tensor #TODO: this could be inside epsilon function perhaps?
            action = epsilon_greedy_action(obs_tensor, epsilon)
            
            next_obs, reward, terminated, truncated, info = env.step(action)    #take the next step
            episode_ended = terminated or truncated                                      #check if crashed or truncuated

            buffer.add(obs_tensor, action, torch.tensor(next_obs), torch.tensor(reward), torch.tensor(float(episode_ended)))
            if DEBUG:
                buffer.printBuffer
                return 1
            
            obs = next_obs                                                          #next step becomes initial step

        
            total_reward += reward                                                  #sum rewards
            steps += 1                                                              #sum steps

    env.close()  


def main():
    training()
    #buffer.printBuffer()
    #buffer.giveRandomBatch(4)


if __name__ == "__main__":
    main()

training()
buffer.printBuffer()
buffer.giveRandomBatch(4)

''' TESTING ZONE '''

''' UNDERSTANDING INPUT AND OUTPUT DEBUGGING

obs, info = env.reset()
print(obs)
obs_tensor = torch.tensor(obs)
q_val = model(obs_tensor)
print(q_val)
action = torch.argmax(q_val).item()
print("action: ", action)
'''


'''  OBSERVATION AND TENSOR
obs, info = env.reset()     #starting state
obs_tensor = torch.tensor(obs)

print(obs_tensor.shape)
'''


''' TESTING EPSILON GREEDY FUNCTION
#three random actions
epsilon_greedy_action(obs_tensor, 1)
epsilon_greedy_action(obs_tensor, 1)
epsilon_greedy_action(obs_tensor, 1)
#three NN actions
epsilon_greedy_action(obs_tensor, 0)
epsilon_greedy_action(obs_tensor, 0)
epsilon_greedy_action(obs_tensor, 0)
'''
 

''' TESTING BUFFER CLASS 
testingBuffer = ExperienceBuffer(5)

for x in range(10):
    testingBuffer.add(x)
    testingBuffer.printBuffer()

print("end state of list: ")
print(testingBuffer.buffer)

print("=== random batch test ===")
batch = testingBuffer.giveRandomBatch(4)
'''