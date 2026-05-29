#input normalisation constants [gymanasium enviroment dependent]
MAX_X = 2.5                     #x position
MAX_Y = 2.5                     #y position
MAX_VELOCITY_X = 10.            #x velocity
MAX_VELOCITY_Y = 10.            #y velocity
MAX_ANGLE = 6.2831855           #angle of ship
MAX_ANGULAR_VELOCITY = 10.      #angular velocity of ship


#constants
NUMBER_OF_EPISODES = 200    # number of training episodes
BUFFER_SIZE = 3000          # size of experience buffer
DEBUG = False               # flag for debug prints
TEMP_DEBUG = False          # another flag for debug, possibly to delete
TRAINING_BATCH_SIZE = 64    # size of random batch from experience buffer for training
LAST_REWARDS_SIZE = 50      # size of list of last reward for calculating mean/model progress in learning
#short note is always written freshly into the report in the function
# this constant might be not needed
MEMO = "basic DQN, training done in batches, no normalisation, only one NN, random batches for better learning"

# hard to update, possibly also should be deleted
NN_LAYOUT = "8->64->RELU->64->RELU->4 (two hidden layers of 64 neurons, ReLU activation function, MSE loss function)"

#possibly to delete
REPORT = True #should training be written into log


#hyperparameters of Q learning [name this better]
ALPHA = 0.1                     #learning rate
GAMMA = 0.99                    #"importance of future"
INITIAL_EPSILON = 0.999         #random move probability
MINIMAL_EPSILON = 0.1
LEARNING_RATE = 0.001       #move this into constants

