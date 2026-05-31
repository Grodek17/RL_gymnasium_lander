import torch.nn as nn

#input normalisation constants [gymanasium enviroment dependent]
MAX_X = 2.5                     #x position
MAX_Y = 2.5                     #y position
MAX_VELOCITY_X = 10.            #x velocity
MAX_VELOCITY_Y = 10.            #y velocity
MAX_ANGLE = 6.2831855           #angle of ship
MAX_ANGULAR_VELOCITY = 10.      #angular velocity of ship


#constants
NUMBER_OF_EPISODES = 6000    # number of training episodes
BUFFER_SIZE = 50000         # size of experience buffer
DEBUG = False               # flag for debug prints
TEMP_DEBUG = False          # another flag for debug, possibly to delete
TRAINING_BATCH_SIZE = 64    # size of random batch from experience buffer for training
LAST_REWARDS_SIZE = 50      # size of list of last reward for calculating mean/model progress in learning


#hyperparameters of Q learning [name this better]
GAMMA = 0.99                    #"importance of future"
INITIAL_EPSILON = 0.9         #random move probability
EPSILON_DECAY_SUBSTRACT = 0.00016 #epsilon reduced by this ammount every episode
MINIMAL_EPSILON = 0.1
LEARNING_RATE = 0.001       #move this into constants
UPDATE_TARGET_EACH_STEPS = 1000

#constants of NN to train
INPUT_SIZE = 8
FIRST_H_LAYER = 128
SECOND_H_LAYER = 128
ACTIVATION_FUNCTION = "ReLU"
OUTPUT_SIZE = 4


#names of activation functions for initialisation of NN
ACTIVATIONS = {
    "ReLU": nn.ReLU,
    "tanh": nn.Tanh,
}