import torch 
import torch.nn as nn

from constants import FIRST_H_LAYER, SECOND_H_LAYER

# Artificial neural network made in pyTorch, used in DQN
class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.first = nn.Linear(8,FIRST_H_LAYER)
        self.ReLU = nn.ReLU()
        self.second = nn.Linear(FIRST_H_LAYER, SECOND_H_LAYER)
        self.last = nn.Linear(SECOND_H_LAYER, 4)
    
    def forward(self, x):
        x = self.first(x)
        x = self.ReLU(x)
        x = self.second(x)
        x = self.ReLU(x)
        x = self.last(x)
        return x