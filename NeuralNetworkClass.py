import torch 
import torch.nn as nn

from constants import ACTIVATIONS


# Artificial neural network made in pyTorch, used in DQN
class NeuralNetwork(nn.Module):
    def __init__(self, input, first_layer, second_layer, output, activation_function, weights_object=None):
        super().__init__()
        self.first = nn.Linear(input, first_layer)
        self.second = nn.Linear(first_layer, second_layer)
        self.last = nn.Linear(second_layer, output)

        if activation_function not in ACTIVATIONS:
            raise ValueError(f"Unknown activation: {activation_function}, check activation dictionary in cobstants.py for valid names")

        self.activation = ACTIVATIONS[activation_function]()

        if weights_object != None:
            self.load_state_dict(weights_object)
    
    def forward(self, x):
        x = self.first(x)
        x = self.activation(x)
        x = self.second(x)
        x = self.activation(x)
        x = self.last(x)
        return x