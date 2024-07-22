import numpy as np
import random as rd
import math
import torch
import torch.nn as nn


class AlphaNet(nn.Module):
    def __init__(self):
        super(AlphaNet, self).__init__()

        self.activation = nn.Sigmoid()

        self.fc1 = nn.Linear(in_features=8, out_features=128)
        self.fc2 = nn.Linear(in_features=128, out_features=256)
        self.fc3 = nn.Linear(in_features=256, out_features=128)
        self.fc4 = nn.Linear(in_features=128, out_features=8)
        self.fc5 = nn.Linear(in_features=8, out_features=2)

    def forward(self, x):
        x = torch.tensor(x)
        x = self.activation(self.fc1(x))
        x = self.activation(self.fc2(x))
        x = self.activation(self.fc3(x))
        x = self.activation(self.fc4(x))
        x = self.activation(self.fc5(x))

        return x