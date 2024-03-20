import torch
import torch.nn as nn

# Define the neural network architecture
class HingstonNetwork(nn.Module):
    def __init__(self):
        super(HingstonNetwork, self).__init__()

        self.conv1 = nn.Conv2d(in_channels=1, out_channels=1,
                               kernel_size=(3, 11), stride=1, padding=0)
        self.conv2 = nn.Conv2d(in_channels=1, out_channels=1,
                               kernel_size=(11, 3), stride=1, padding=0)
        self.conv3 = nn.Conv2d(in_channels=1, out_channels=1,
                               kernel_size=(3, 3), stride=1, padding=0)
        self.fc1 = nn.Linear(99, 10)
        self.fc2 = nn.Linear(10, 1)

    def forward(self, x_grid):
        horizontal_strip = torch.flatten(self.conv1(x_grid))
        vertical_strip = torch.flatten(self.conv2(x_grid))
        patch3x3 = torch.flatten(self.conv3(x_grid))
        x = torch.cat((horizontal_strip, vertical_strip, patch3x3))
        x = self.fc1(x)
        x = self.fc2(x)

        return x
