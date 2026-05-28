# to check:
# is leaarning working correctly -> print + manual calculation of small batch (e.g) 3 Q(s,a) and target
# is Q(s,a) taking proper actions
# check if target is calculated without gradient
# check if optimizer changes weights
# test one transiton overfit, if training on one record will make it fitting
# test if model learning is actually happening
# do something to make it faster
import gymnasium
import random
import torch 
import torch.nn as nn
import numpy as np
import time


#constants
NUMBER_OF_EPISODES = 3000
BUFFER_SIZE = 3000
DEBUG = False
TEMP_DEBUG = False
TRAINING_BATCH_SIZE = 64
LAST_REWARDS_SIZE = 50


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

        if len(self.buffer) < (TRAINING_BATCH_SIZE * 2):
            raise ValueError("Buffer not full, cannot give random batch", len(self.buffer), "<- buffer lenght | full size (-5) -> ", (self.buffersize - 5))

        packed_observations = []
        packed_actions = []
        packed_nexts = []
        packed_reward = []
        packed_dones = []

        rangex = len(self.buffer)
        for x in range(batch_size):
            index = random.randint(0, (rangex - 1))
            packed_observations.append(self.buffer[index][0])
            packed_actions.append(self.buffer[index][1])
            packed_nexts.append(self.buffer[index][2])
            packed_reward.append(float(self.buffer[index][3]))
            packed_dones.append(float(self.buffer[index][4]))

        #conversions to numpy arrays
        packed_observations = np.array(packed_observations, dtype=np.float32)
        packed_actions = np.array(packed_actions, dtype=np.int64)
        packed_nexts = np.array(packed_nexts, dtype=np.float32)
        packed_reward = np.array(packed_reward, dtype=np.float32)
        packed_dones = np.array(packed_dones, dtype=np.float32)

        #turning into tensors (tutaj zamiana z torch.tensor(x) na torch.from_numpy(x)??)
        packed_observations = torch.from_numpy(packed_observations)
        packed_actions = torch.from_numpy(packed_actions)
        packed_nexts = torch.from_numpy(packed_nexts)
        packed_reward = torch.from_numpy(packed_reward)
        packed_dones = torch.from_numpy(packed_dones)

        if TEMP_DEBUG:
            print(packed_observations.shape, packed_observations.dtype)
            print(packed_actions.shape, packed_actions.dtype)
            print(packed_nexts.shape, packed_nexts.dtype)
            print(packed_reward.shape, packed_reward.dtype)
            print(packed_dones.shape, packed_dones.dtype)
            print("============================= END ====================")
            raise ValueError("debug new converion")
            
        
        return packed_observations, packed_actions, packed_nexts, packed_reward, packed_dones

    
    def printBuffer(self):
        print("=== PRINT STARTED ===")
        for x in range(len(self.buffer)):
            print(x, ": ", self.buffer[x])


lrate = 0.001
model = NeuralNetwork()
buffer = ExperienceBuffer(BUFFER_SIZE)
#ready loss and backpropagating functions
#loss_fn = nn.MSELoss()
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
    #print("model learning activated")
    startbatch = time.perf_counter()
    obs, actions, nexts, rewards, dones = buffer.giveRandomBatch(TRAINING_BATCH_SIZE)
    endbatch = time.perf_counter()
    print("batchtime:", endbatch - startbatch, "s")
    Qvalues = model(obs)
    unsqueezed_actions = actions.unsqueeze(1)
    Qsa = Qvalues.gather(1, unsqueezed_actions).squeeze(1)


    with torch.no_grad():
        nextQs = model(nexts)
        best_moves = nextQs.max(dim = 1).values


    
    #print("nextQs: ", nextQs)
    #print("Choosen Q: ", best_moves)
    target = rewards + GAMMA * (1 - dones) * best_moves

    #MSE
    loss = ((Qsa - target)**2).mean()
    '''
    print("== target debug ==")
    print("target shape: ", target.shape)
    print("Qsa shape: ", Qsa.shape)
    print("loss shape: ", loss.shape)
    print("loss: ", loss)
    raise ValueError("checkking if loss is proper")
    '''
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
    lastrewards = []
    mean_rewards = []
    number_of_episode = []
    epsilon = INITIAL_EPSILON
    for episode in range(NUMBER_OF_EPISODES):
        if episode % 10 == 0:
            print("episode: ", episode)
        obs, info = env.reset()             #starting state
        episode_ended = False
        total_reward = 0
        steps = 0
        epsilon = max((epsilon - 0.0001), MINIMAL_EPSILON)

        startepisode = time.perf_counter()
        while not episode_ended:
            #turning observation into tensor #TODO: this could be inside epsilon function perhaps?
            action = epsilon_greedy_action(torch.tensor(obs), epsilon)
            
            next_obs, reward, terminated, truncated, info = env.step(action)    #take the next step
            episode_ended = terminated or truncated                                      #check if crashed or truncuated

            buffer.add(obs, action, next_obs, reward, episode_ended)
            #buffer.printBuffer()
            
            if DEBUG:
                #buffer.printBuffer
                #return 1
                pass

            #training step
            #print("debug [training() before modellearning()]: buffer.buffer lenght: ", len(buffer.buffer), "buffer.buffersize: ", buffer.buffersize )
            if len(buffer.buffer) > ((TRAINING_BATCH_SIZE * 2)+ 1):
                 startlearning = time.perf_counter()
                 modelLearning()
                 endelearning = time.perf_counter()
                 print("episodetime:", endelearning - startlearning, "s")
             #    print(".")
                 
            

            obs = next_obs                                                          #next step becomes initial step

        
            total_reward += reward                                                  #sum rewards
            steps += 1          
            if(terminated or truncated):
                #print("episode: ", episode, " total reward: ", total_reward) 

                #updating the episode reward buffer
                if len(lastrewards) > LAST_REWARDS_SIZE:
                    lastrewards.pop(0)
                lastrewards.append(total_reward)

                if episode % 50 == 0:
                    meanlastreward = sum(lastrewards)/float(len(lastrewards))
                    mean_rewards.append(meanlastreward)
                    number_of_episode.append(episode)

                    print("[D]: (epsilon: ", epsilon, ") episode: ", number_of_episode[-1], " mean 50 rewards: ", mean_rewards[-1])
            endepisode = time.perf_counter()
            print("episodetime:", endepisode - startepisode, "s")


    env.close()  
    print("mean rewards: ", mean_rewards)


def main():
    training()
    #buffer.printBuffer()
    #print("ilosc rekordow:",len(buffer.buffer))
    #buffer.giveRandomBatch(11)
    #modelLearning()
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