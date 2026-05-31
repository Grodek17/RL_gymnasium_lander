# Class for storing all parameters of network, training process and Q learning
# used in rebuilding network from file and reports
class NetworkSave():
    def __init__(self, best_reward, input_size, first_layer, second_layer, activation_function, output, 
                 num_of_train, buff_size, batch_size, net_update_each, mean_reward_episodes, gamma, initial_epsilon,
                 epsilon_subtract, minimal_epsilon, lRate, saved_wghts_torch):
        #TODO: is savefile name needed?
        self.best_reward_training = best_reward

        # Network details
        self.input_size = input_size
        self.first_layer_size = first_layer
        self.second_layer_size = second_layer
        self.activation = activation_function
        self.output_size = output

        # Training details
        self.num_of_training_eps = num_of_train
        self.buffer_size = buff_size
        self.batch_size = batch_size
        self.network_update_each = net_update_each
        self.mean_reward_each = mean_reward_episodes

        # Q learning details
        self.gamma = gamma
        self.initial_epsilon = initial_epsilon
        self.epsilon_subtract = epsilon_subtract
        self.min_epsilon = minimal_epsilon
        self.learning_rate = lRate

        # network weights 
        self.saved_weights_torch = saved_wghts_torch

