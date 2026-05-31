import torch 
import torch.nn as nn

ACTIVATIONS = {
    "relu": nn.ReLU,
    "tanh": nn.Tanh,
}


# Artificial neural network made in pyTorch, used in DQN
class NeuralNetwork(nn.Module):
    def __init__(self, input, first_layer, second_layer, output, activation_function):
        super().__init__()
        self.first = nn.Linear(input, first_layer)
        self.second = nn.Linear(first_layer, second_layer)
        self.last = nn.Linear(second_layer, output)

        if activation_function == "ReLU":
            self.activation = nn.ReLU()
        else:
            self.activation = nn.ReLU()
    
    def forward(self, x):
        x = self.first(x)
        x = self.activation(x)
        x = self.second(x)
        x = self.activation(x)
        x = self.last(x)
        return x