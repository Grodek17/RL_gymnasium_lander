# to check:
# [checked] corectness of target and loss calculation
# check if target is calculated without gradient
# check if optimizer changes weights
# [checked] single observation learning
import gymnasium
import random
import torch 
import torch.nn as nn
import numpy as np
import time
import matplotlib.pyplot as plt


#constants
NUMBER_OF_EPISODES = 5000
BUFFER_SIZE = 3000
DEBUG = False
TEMP_DEBUG = False
TRAINING_BATCH_SIZE = 64
LAST_REWARDS_SIZE = 50
MEMO = "basic DQN, training done in batches, no normalisation, only one NN, random batches for better learning"
NN_LAYOUT = "8->64->RELU->64->RELU->4 (two hidden layers of 64 neurons, ReLU activation function, MSE loss function)"
REPORT = True #should training be written into log


#hyperparameters of Q learning
ALPHA = 0.1         #learning rate
GAMMA = 0.99        #"importance of future"
INITIAL_EPSILON = 0.999       #random move probability
MINIMAL_EPSILON = 0.1
lrate = 0.001

''' CLASSES '''
# Artificial neural network made in pyTorch, used in DQN
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
        self.buffermaxsize = max_size
        self.buffer = []


    #arguments passed as arrays and int's, not always used in batch -> no need to transform (improved time efficiency)
    def add(self, observation, action, next_observation, reward, done):
        if(len(self.buffer) > self.buffermaxsize):
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
            raise ValueError("Buffer not full, cannot give random batch", len(self.buffer), "<- buffer lenght | full size (-5) -> ", (self.buffermaxsize - 5))

        #later could start as numpy arrays, faster computation perhaps?
        packed_observations = []
        packed_actions = []
        packed_nexts = []
        packed_reward = []
        packed_dones = []

        currentbufferlen = len(self.buffer)
        for x in range(batch_size):
            index = random.randint(0, (currentbufferlen - 1))
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

        #turning into tensors 
        packed_observations = torch.from_numpy(packed_observations)
        packed_actions = torch.from_numpy(packed_actions)
        packed_nexts = torch.from_numpy(packed_nexts)
        packed_reward = torch.from_numpy(packed_reward)
        packed_dones = torch.from_numpy(packed_dones)

        if DEBUG:
            print(packed_observations.shape, packed_observations.dtype)
            print("============================= END ====================")
            #raise ValueError("debug new converion")
            
        
        return packed_observations, packed_actions, packed_nexts, packed_reward, packed_dones

    
    def printBuffer(self):
        print("=== PRINT STARTED ===")
        for x in range(len(self.buffer)):
            print(x, ": ", self.buffer[x])

''' CLASSES INITIALISATION '''
learning_model = NeuralNetwork()
target_model = NeuralNetwork()
target_model.load_state_dict(learning_model.state_dict())


buffer = ExperienceBuffer(BUFFER_SIZE)
optimizer = torch.optim.Adam(learning_model.parameters(), lr=lrate)
env = gymnasium.make("LunarLander-v3", continuous=False, gravity=-10.0, enable_wind=False, wind_power=15.0, turbulence_power=0.5)





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
            qvalues = learning_model(x)
            action = torch.argmax(qvalues).item()
        if DEBUG:
            #print("Model determined: qValues: ", qvalues, " action: ", action)
            pass

    return action

def modelLearning():
    #print("model learning activated")
    obs, actions, nexts, rewards, dones = buffer.giveRandomBatch(TRAINING_BATCH_SIZE)

    
    Qvalues = learning_model(obs)
    unsqueezed_actions = actions.unsqueeze(1)
    Qsa = Qvalues.gather(1, unsqueezed_actions).squeeze(1)
    
    with torch.no_grad():
        nextQs = target_model(nexts)
        best_moves = nextQs.max(dim = 1).values
          

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

     print("== target debug ==")
    print("target shape: ", target.shape)
    print("Qsa shape: ", Qsa.shape)
    print("loss shape: ", loss.shape)
    print("loss: ", loss)
    raise ValueError("checkking if loss is proper")

    #print("nextQs: ", nextQs)
    #print("Choosen Q: ", best_moves)
    '''
    
def reportResults(episode_list, mean_list, epsilon_list):
    print("please give name of the plot title:")
    name = input()
    print("please give name of the plot file:")
    filename = input()

    ''' PLOT '''
    plt.plot(episode_list, mean_list, marker="o")
    plt.xlabel("Episode")
    plt.ylabel(f"mean reward of last {LAST_REWARDS_SIZE} episodes")
    plt.title(name)
    plt.grid(True)
    plt.savefig(filename + ".png")
    plt.show()

    ''' MARKDOWN UPDATE '''
    print("Write title of report section in markdown file: ")
    title = input()
    print("please write note about this specific training: ")
    note = input()
    with open("report_data.md", "a", encoding="utf-8") as file:
        file.write(f"#=== REPORT: {title} ===\n\n")
        file.write(f"note: {note}\n")
        file.write(f"memo: {MEMO}\n")
        file.write(f"NN Layout: {NN_LAYOUT}\n")
        file.write(f"Number of episodes: {NUMBER_OF_EPISODES}\n")
        file.write(f"Buffer size: {BUFFER_SIZE}\n")
        file.write(f"Batch size: {TRAINING_BATCH_SIZE}\n")
        file.write(f"Gamma: {GAMMA}\n")
        file.write(f"Learning rate: {lrate}\n\n")

        file.write("## Mean rewards\n\n")

        for episode, reward, epsilon in zip(episode_list, mean_list, epsilon_list):
            file.write(f"- Episode {episode}: {reward:.2f}, epsilon: {epsilon:.2f}\n")
        file.write("#================\n\n")


#main loop of training in the enviroment
def training():
    lastrewards = []
    mean_rewards = []
    number_of_episode = []
    epsilon_list = []
    epsilon = INITIAL_EPSILON
    for episode in range(NUMBER_OF_EPISODES):
        if episode % 20 == 0:
            print("episode: ", episode)
        obs, info = env.reset()             #starting state
        episode_ended = False
        total_reward = 0
        steps = 0
        epsilon = max((epsilon - 0.0001), MINIMAL_EPSILON)

        #updating target model:
        if episode % 100 == 0:
            target_model.load_state_dict(learning_model.state_dict())

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
            #print("debug [training() before modellearning()]: buffer.buffer lenght: ", len(buffer.buffer), "buffer.buffermaxsize: ", buffer.buffermaxsize )
            if len(buffer.buffer) > ((TRAINING_BATCH_SIZE * 2)+ 1):
                 modelLearning()
                 

            obs = next_obs                                                          #next step becomes initial step
            total_reward += reward                                                  #sum rewards
            steps += 1          
            if(terminated or truncated):

                #updating the episode reward buffer
                if len(lastrewards) > LAST_REWARDS_SIZE:
                    lastrewards.pop(0)
                lastrewards.append(total_reward)
                if episode % 50 == 0:
                    meanlastreward = sum(lastrewards)/float(len(lastrewards))
                    mean_rewards.append(float(meanlastreward))
                    number_of_episode.append(float(episode))
                    epsilon_list.append(float(epsilon))

                    print("[D]: (epsilon: ", epsilon, ") episode: ", number_of_episode[-1], " mean ", LAST_REWARDS_SIZE ," rewards: ", mean_rewards[-1])
            


    env.close()  
    print("mean rewards: ", mean_rewards)
    if REPORT:
        reportResults(number_of_episode, mean_rewards, epsilon_list)


def main():
    #modelLearning()
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