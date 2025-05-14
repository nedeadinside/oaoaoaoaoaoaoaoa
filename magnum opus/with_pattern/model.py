import torch
import torch.nn as nn
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.LazyConv2d(32, kernel_size=5, stride=2),
            nn.RReLU(),
            nn.MaxPool2d(2),
            nn.LazyConv2d(64, kernel_size=3),
            nn.RReLU(),
            nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.LazyLinear(256),
            nn.ReLU(),
            nn.LazyLinear(10)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

    def predict_proba(self, x):
        with torch.inference_mode():
            output = self(x)
            probabilities = F.softmax(output, dim=1)
        return probabilities

    def load_model(self, path):
        self.load_state_dict(torch.load(path, map_location="cpu"))
        self.eval()