import gymnasium
import random
import torch 
import torch.nn as nn


#constants
NUMBER_OF_EPISODES = 300
BUFFER_SIZE = 10
DEBUG = True
TRAINING_BATCH_SIZE = 3


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
                #print("List approached full capacity, removing oldest record")
                pass
            self.buffer.pop(0)
        
        self.buffer.append((observation, action, next_observation, reward, done))

    #provides batch of separate vectors of each attribute, used in later computing
    def giveRandomBatch(self, batch_size):
        if DEBUG:
            print("selecting batch_size random entries from list")

        if len(self.buffer) < (self.buffersize - 1):
            raise ValueError("Buffer not full, cannot give random batch")

        packed_observations = []
        packed_actions = []
        packed_nexts = []
        packed_reward = []
        packed_dones = []
        for x in range(batch_size):
            index = random.randint(0, self.buffersize - 1)
            packed_observations.append(self.buffer[index][0])
            packed_actions.append(self.buffer[index][1])
            packed_nexts.append(self.buffer[index][2])
            packed_reward.append(self.buffer[index][3])
            packed_dones.append(self.buffer[index][4])
        
        #turning into tensors
        packed_observations = torch.stack(packed_observations)
        packed_actions = torch.stack(packed_actions)
        packed_nexts = torch.stack(packed_nexts)
        packed_reward = torch.stack(packed_reward)
        packed_dones = torch.stack(packed_dones)

        if DEBUG:
            print(packed_observations.shape, packed_observations.dtype)
            print(packed_actions.shape, packed_actions.dtype)
            print(packed_nexts.shape, packed_nexts.dtype)
            print(packed_reward.shape, packed_reward.dtype)
            print(packed_dones.shape, packed_dones.dtype)
            
        
        return packed_observations, packed_actions, packed_nexts, packed_reward, packed_dones

    
    def printBuffer(self):
        print("=== PRINT STARTED ===")
        for x in range(len(self.buffer)):
            print(x, ": ", self.buffer[x])


lrate = 0.001
model = NeuralNetwork()
buffer = ExperienceBuffer(BUFFER_SIZE)
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
            #print("Random action selected: ", action)
            pass
    else:
        with torch.no_grad():               
            qvalues = model(x)
            action = torch.argmax(qvalues).item()
        if DEBUG:
            #print("Model determined: qValues: ", qvalues, " action: ", action)
            pass

    return action

def modelLearning():
    obs, actions, nexts, rewards, dones = buffer.giveRandomBatch(TRAINING_BATCH_SIZE)
    Qvalues = model(obs)
    unsqueezed_actions = actions.unsqueeze(1)
    Qsa = Qvalues.gather(1, unsqueezed_actions)


    with torch.no_grad():
        nextQs = model(nexts)
        best_moves = nextQs.max(dim = 1).values


    
    #print("nextQs: ", nextQs)
    #print("Choosen Q: ", best_moves)
    target = rewards + GAMMA * (1 - dones) * best_moves

    #MSE
    loss = ((Qsa - target)**2).mean()
    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()




    '''
    print("== target debug ==")
    print("target shape: ", target.shape)
    print("rewards shape: ", rewards.shape)
    print("dones shape: ", dones.shape)
    print("best_moves shape: ", best_moves.shape)
    print("=====")
    print("rewards: ", rewards)
    print("gamma", GAMMA)
    print("dones", dones)
    print("best: ", best_moves)
    print("equals target: ", target)
    '''
    

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

            buffer.add(obs_tensor, torch.tensor(action), torch.tensor(next_obs), torch.tensor(reward, dtype=torch.float32), torch.tensor(float(episode_ended)))
            if DEBUG:
                #buffer.printBuffer
                #return 1
                pass

            #training step
            '''
                if len(buffer.buffer) < buffer.buffersize:
                 modelLearning()
            '''

            obs = next_obs                                                          #next step becomes initial step

        
            total_reward += reward                                                  #sum rewards
            steps += 1                                                              #sum steps

    env.close()  


def main():
    training()
    #buffer.printBuffer()
    #print("ilosc rekordow:",len(buffer.buffer))
    #buffer.giveRandomBatch(11)
    modelLearning()
    pass



if __name__ == "__main__":
    main()




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



training()
buffer.printBuffer()
buffer.giveRandomBatch(4)
'''


''' TESTING TUPLE UNPACKING
    lista = [("Pawel", 18, "student"), ("Kasia", 20, "studentka"), ("Mateusz", 28, "worker"), ("John", 128, "dziads")]
    imiona = []
    wieki = []
    zawody = []
    for x in range(4):
        imiona.append(lista[x][0])
        wieki.append(lista[x][1])
        zawody.append(lista[x][2])

    print("imiona odpakowane: ", imiona)
'''