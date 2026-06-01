#todo
# training functions as class
# paths as constants
# training functions as a separate file
# saving videos of trained network via gymnasium
# src folder with all code
# choose what to do in main switch/input
# todo save loss functino
import gymnasium
import random
import torch 
import torch.nn as nn
import numpy as np
import time
import matplotlib.pyplot as plt
import copy

from datetime import datetime
from NeuralNetworkClass import NeuralNetwork
from ExperienceBufferClass import ExperienceBuffer
from Network_save_class import NetworkSave

from helpers import normalise_observation
from eval import evaluation

from constants import (NUMBER_OF_EPISODES, ACTIVATION_FUNCTION, INPUT_SIZE, OUTPUT_SIZE, EPSILON_DECAY_SUBSTRACT,
                       BUFFER_SIZE, DEBUG, TRAINING_BATCH_SIZE, FIRST_H_LAYER, SECOND_H_LAYER,
                       LAST_REWARDS_SIZE, GAMMA, UPDATE_TARGET_EACH_STEPS,
                       INITIAL_EPSILON, MINIMAL_EPSILON ,LEARNING_RATE)

''' CLASSES INITIALISATION '''
learning_model = NeuralNetwork(INPUT_SIZE, FIRST_H_LAYER, SECOND_H_LAYER, OUTPUT_SIZE, ACTIVATION_FUNCTION, weights_object = None)
target_model = NeuralNetwork(INPUT_SIZE, FIRST_H_LAYER, SECOND_H_LAYER, OUTPUT_SIZE, ACTIVATION_FUNCTION, weights_object = None)
target_model.load_state_dict(learning_model.state_dict())

buffer = ExperienceBuffer(BUFFER_SIZE)
optimizer = torch.optim.Adam(learning_model.parameters(), lr=LEARNING_RATE)

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
    


def reportResults(episode_list, mean_list, epsilon_list, saved_training):
    ''' ASKING TO SAVE '''
    while True:
        print("save plot, report and network? [y/n]")
        save = input()
        if save == "y":
            break
        elif save == "n":
            return
        
    print("please give file name of the plot title, plot file and NN file (same for all for better navigation):")
    name = input()
    filename = name
    networkfile_name = name

    ''' PLOT '''
    plt.plot(episode_list, mean_list)
    plt.xlabel("Episode")
    plt.ylabel(f"mean reward of last {saved_training.mean_reward_each} episodes")
    plt.title(name)
    plt.grid(True)
    plt.savefig("plots/" + filename + ".png")
    plt.show()

    ''' SAVING NN '''
    torch.save(saved_training.__dict__, "trained_networks/"+ networkfile_name +".pth")

    ''' MARKDOWN UPDATE '''
    print("Write title of report section in markdown file: ")
    title = input()
    print("please write note about this specific training: ")
    note = input()

    time = datetime.now().strftime("%Y:%m:%d:%H:%M")
    with open("report_data.md", "a", encoding="utf-8") as file:
        file.write(f"#=== REPORT: {title} ===\n")
        file.write(f"Report date: {time} \n\n")
        file.write(f"network saved as: {networkfile_name}.pth \n")
        file.write(f"best reward scored by network: **{saved_training.best_reward_training}** \n")
        file.write(f"note: {note} \n \n")

        file.write("=== network details ===\n")
        file.write(f"Input size: {saved_training.input_size}\n")
        file.write(f"First hidden layer size: {saved_training.first_layer_size}\n")
        file.write(f"Second hidden layer: {saved_training.second_layer_size}\n")
        file.write(f"activation function: {saved_training.activation}\n")
        file.write(f"output size: {saved_training.output_size}\n")
        file.write(f"network 'graph': {saved_training.input_size} -> {saved_training.first_layer_size} -> {saved_training.activation} -> {saved_training.second_layer_size} -> {saved_training.activation} -> {saved_training.output_size}\n\n")

        file.write(f"=== training details ===\n")
        file.write(f"Number of training episodes: {saved_training.num_of_training_eps}\n")
        file.write(f"Buffer size: {saved_training.buffer_size}\n")
        file.write(f"Batch size: {saved_training.batch_size}\n")
        file.write(f"Target network updated each {saved_training.network_update_each} steps \n \n")

        file.write(f"=== Q learning parameters ===\n")
        file.write(f"Gamma: {saved_training.gamma}\n")
        file.write(f"Initial epsilon: {saved_training.initial_epsilon} \n")
        file.write(f"Epsilon lowered each episode by {saved_training.epsilon_subtract}\n")
        file.write(f"Minimal epsilon: {saved_training.min_epsilon} \n")
        file.write(f"Learning rate: {saved_training.learning_rate}\n\n")
        file.write("![Training plot](plots/" + filename + ".png)\n\n")
        file.write("## Mean rewards\n\n")

        for episode, reward, epsilon in zip(episode_list, mean_list, epsilon_list):
            if episode % 500 == 0:
                file.write(f"- Episode {episode:.0f}: {reward:.2f}, epsilon: {epsilon:.2f}\n")
        file.write("\n\n")

#main loop of training in the enviroment
def training():
    env = gymnasium.make("LunarLander-v3", continuous=False, gravity=-10.0, enable_wind=False, wind_power=15.0, turbulence_power=0.5)
    lastrewards = []
    mean_rewards = []
    number_of_episode = []
    epsilon_list = []
    epsilon = INITIAL_EPSILON
    global_step = 0
    best_reward = -999999


    for episode in range(NUMBER_OF_EPISODES):
        if episode % 1000 == 0:
            episode_start_time = time.perf_counter()
        obs, info = env.reset()             #starting state
        obs = normalise_observation(obs)

        episode_steps = 0
        episode_ended = False
        total_reward = 0
        epsilon = max((epsilon - EPSILON_DECAY_SUBSTRACT), MINIMAL_EPSILON)

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

    # save all metadata of a training, structure of NN, hyperparameters, etc
    saved_training = NetworkSave(best_reward, INPUT_SIZE, FIRST_H_LAYER, SECOND_H_LAYER, ACTIVATION_FUNCTION, OUTPUT_SIZE, NUMBER_OF_EPISODES, BUFFER_SIZE, TRAINING_BATCH_SIZE,
                                 UPDATE_TARGET_EACH_STEPS, LAST_REWARDS_SIZE, GAMMA, INITIAL_EPSILON, EPSILON_DECAY_SUBSTRACT, MINIMAL_EPSILON, LEARNING_RATE, best_model_state)
    
    #change to saved training
    reportResults(number_of_episode, mean_rewards, epsilon_list, saved_training)


def main():
    #training()
    evaluation(5, "trained_networks/64_relu_2nd.pth", random_baseline=False, record_video=True)
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