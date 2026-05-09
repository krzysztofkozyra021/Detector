import tensorflow as tf
import torch
import torch.nn as nn
import torch.nn.functional as F

from tensorflow.keras import layers, models


def create_model(input_shape=(64, 64, 3), num_classes=21):
    """
    Creates a CNN model for Polish traffic signs (21-class) classification.
    Expects input shape of 64x64 RGB images.
    """
    model = models.Sequential(
        [
            layers.Conv2D(32, (3, 3), activation="relu", input_shape=input_shape),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"]
    )

    return model


class SignModelPyTorch(nn.Module):
    def __init__(self, num_classes=92):
        super(SignModelPyTorch, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=5, padding=2),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(64, 128, kernel_size=5, padding=2),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )

        self.classifier = nn.Sequential(
            nn.Linear(256 * 4 * 4, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


class SignDetectorCNN(nn.Module):
    """CNN do detekcji znaków - binary classification (ZNAK vs NIE-ZNAK)"""
    
    def __init__(self):
        super(SignDetectorCNN, self).__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
        )
        
        self.classifier = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256 * 8 * 8, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(512, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            # Final output for 2 classes (sign vs no-sign)
            nn.Linear(128, 2)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x


def load_trained_model(path="polskie_znaki_model_92.pth"):
    """
    Loads a pre-trained model from disk (supports .h5 for Keras and .pth for PyTorch).
    """
    try:
        if path.endswith(".pth"):
            # Load PyTorch model
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            loaded_data = torch.load(path, map_location=device)

            if isinstance(loaded_data, torch.nn.Module):
                # Saved using torch.save(model, path)
                model = loaded_data
            elif isinstance(loaded_data, dict):
                # Saved using torch.save(model.state_dict(), path)
                # We assume it's our SignModelPyTorch with 92 classes based on the filename
                model = SignModelPyTorch(num_classes=92)
                model.load_state_dict(loaded_data)
            else:
                raise ValueError(f"Unknown data type in .pth file: {type(loaded_data)}")

            model.to(device)
            model.eval()
            print(f"Loaded PyTorch model from {path}")
            return model
        else:
            # Load Keras model
            model = tf.keras.models.load_model(path)
            print(f"Loaded Keras model from {path}")
            return model
    except Exception as e:
        print(f"Could not load model from {path}. Error: {e}")
        return None

