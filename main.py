#todo
# check episode and step lenght every 100 episodes
# save model with best mean rewards in case learning "collapses"
# save model in general
# better NN initialisation, no magic numbers
# bigger buffer
# 
# eval function
# reading networks from file (possibly separate .py)
# training functions as class

import gymnasium
import random
import torch 
import torch.nn as nn
import numpy as np
import time
import matplotlib.pyplot as plt
import copy

from NeuralNetworkClass import NeuralNetwork
from ExperienceBufferClass import ExperienceBuffer

from constants import (MAX_X, MAX_Y, MAX_VELOCITY_X, MAX_VELOCITY_Y,
                       MAX_ANGLE, MAX_ANGULAR_VELOCITY, NUMBER_OF_EPISODES,
                       BUFFER_SIZE, DEBUG, TEMP_DEBUG, TRAINING_BATCH_SIZE, FIRST_H_LAYER, SECOND_H_LAYER,
                       LAST_REWARDS_SIZE, ALPHA, GAMMA, UPDATE_TARGET_EACH_STEPS,
                       INITIAL_EPSILON, MINIMAL_EPSILON ,LEARNING_RATE)

''' CLASSES INITIALISATION '''
learning_model = NeuralNetwork()
target_model = NeuralNetwork()
target_model.load_state_dict(learning_model.state_dict())


buffer = ExperienceBuffer(BUFFER_SIZE)
optimizer = torch.optim.Adam(learning_model.parameters(), lr=LEARNING_RATE)
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
    #get random batch of experiences
    obs, actions, nexts, rewards, dones = buffer.giveRandomBatch(TRAINING_BATCH_SIZE)

    #calculate Q(s,a), target and loss
    Qvalues = learning_model(obs)
    unsqueezed_actions = actions.unsqueeze(1)
    Qsa = Qvalues.gather(1, unsqueezed_actions).squeeze(1)
    
    with torch.no_grad():
        nextQs = target_model(nexts)
        best_moves = nextQs.max(dim = 1).values
          
    target = rewards + GAMMA * (1 - dones) * best_moves

    #MSE
    loss = ((Qsa - target)**2).mean()

    #pytorch learning functions    
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    '''
    print("== target debug ==")
    print("target shape: ", target.shape)
    print("best: ", best_moves)
    print("equals target: ", target)
    '''
    
def normalise_observation(obs):
    obs[0] = obs[0]/MAX_X
    obs[1] = obs[1]/MAX_Y
    obs[2] = obs[2]/MAX_VELOCITY_X
    obs[3] = obs[3]/MAX_VELOCITY_Y
    obs[4] = obs[4]/MAX_ANGLE
    obs[5] = obs[5]/MAX_ANGULAR_VELOCITY
    return obs

def reportResults(episode_list, mean_list, epsilon_list, best_network):
    ''' ASKING TO SAVE '''
    while True:
        print("save plot & report? [y/n]")
        save = input()
        if save == "y":
            break
        elif save == "n":
            return
    print("please give name of the plot title:")
    name = input()
    print("please give name of the plot file:")
    filename = input()
    print("please give name of trained NN file: ")
    networkfile_name = input()

    ''' PLOT '''
    plt.plot(episode_list, mean_list, marker="o")
    plt.xlabel("Episode")
    plt.ylabel(f"mean reward of last {LAST_REWARDS_SIZE} episodes")
    plt.title(name)
    plt.grid(True)
    plt.savefig("plots/" + filename + ".png")
    plt.show()

    ''' SAVING NN '''
    torch.save(best_network, "trained_networks/"+ networkfile_name +".pth")

    ''' MARKDOWN UPDATE '''
    print("Write title of report section in markdown file: ")
    title = input()
    print("please write note about this specific training: ")
    note = input()
    with open("report_data.md", "a", encoding="utf-8") as file:
        file.write(f"#=== REPORT: {title} ===\n\n")
        file.write(f"note: {note}\n")
        file.write("---------------------\n")
        file.write(f"Number of episodes: {NUMBER_OF_EPISODES}\n")
        file.write(f"Buffer size: {BUFFER_SIZE}\n")
        file.write(f"Batch size: {TRAINING_BATCH_SIZE}\n")
        file.write(f"First hidden layer size: {FIRST_H_LAYER}\n")
        file.write(f"Second hidden layer: {SECOND_H_LAYER}\n")
        file.write(f"Gamma: {GAMMA}\n")
        file.write(f"Learning rate: {LEARNING_RATE}\n\n")
        file.write("![Training plot](plots/" + filename + ".png)\n\n")
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
    global_step = 0
    best_reward = -999999


    for episode in range(NUMBER_OF_EPISODES):
        #if episode % 10 == 0:
         #   print("episode: ", episode)

        if episode % 1000 == 0:
            episode_start_time = time.perf_counter()
        obs, info = env.reset()             #starting state
        obs = normalise_observation(obs)

        episode_steps = 0
        episode_ended = False
        total_reward = 0
        epsilon = max((epsilon - 0.00016), MINIMAL_EPSILON)

        while not episode_ended:
            if episode_steps == 0 and episode % 1000 == 0:
                #print("registered step start")
                step_start_time = time.perf_counter()
            
            action = epsilon_greedy_action(torch.tensor(obs), epsilon)
            
            next_obs, reward, terminated, truncated, info = env.step(action)    #take the next step
            next_obs = normalise_observation(next_obs)
            episode_ended = terminated or truncated                                      #check if crashed or truncuated

            buffer.add(obs, action, next_obs, reward, episode_ended)

            #training step
            if buffer.current_size > ((TRAINING_BATCH_SIZE * 2)+ 1):
                 modelLearning()
                 

            obs = next_obs                                                          #next step becomes initial step
            total_reward += reward                                                  #sum rewards     
            global_step += 1
            

            #updating target model:
            if global_step >= UPDATE_TARGET_EACH_STEPS:
                target_model.load_state_dict(learning_model.state_dict())
                global_step = 0

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
                    print("Episode: ", number_of_episode[-1], " | mean rewards: ", mean_rewards[-1], " | epsilon: ", epsilon, " |")

                    ###saving the best performing model
                    if meanlastreward > best_reward:
                        print("last best: ", best_reward, " current_best: ", meanlastreward, " saving...")
                        best_model_state = copy.deepcopy(learning_model.state_dict())
                        best_reward = meanlastreward
                        


            if episode_steps == 0 and episode % 1000 == 0:
                #print("registered step stop")
                step_end_time = time.perf_counter()
            episode_steps += 1

       
        if episode % 1000 == 0:
            episode_end_time = time.perf_counter()
            print("episode ", episode, " time: ", episode_end_time - episode_start_time, "s 1st step time: ", step_end_time - step_start_time, "s")
            


    env.close()  
    print("mean rewards: ", mean_rewards)
    
    reportResults(number_of_episode, mean_rewards, epsilon_list, best_model_state)


def main():
    training()
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