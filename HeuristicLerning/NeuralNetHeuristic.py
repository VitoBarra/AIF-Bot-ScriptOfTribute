import torch
import torch.nn as nn


# Fully connected network
class MMHVR_net(nn.Module):
    def __init__(self, input_size):
        super().__init__()
        self.input_size = input_size

        # Layers
        self.fc1 = nn.Linear(input_size, input_size)   # Hidden layer same size
        self.hl1 = nn.Sigmoid(input_size, 30)            # Output layer (single neuron)
        self.hl1 = nn.Sigmoid(input_size, 20)            # Output layer (single neuron)
        self.out = nn.Linear(input_size, 1)  # Output layer (single neuron)

    def forward(self, x):
        x = self.fc1(x)
        x = self.activation(x)
        x = self.out(x)
        return x






