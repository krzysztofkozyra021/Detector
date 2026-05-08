import tensorflow as tf
from tensorflow.keras import layers, models


def create_model(input_shape=(64, 64, 3), num_classes=43):
    """
    Creates a CNN model for GTSRB 43-class classification.
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


def load_trained_model(path="model.h5"):
    """
    Loads a pre-trained model from disk.
    """
    try:
        model = tf.keras.models.load_model(path)
        return model
    except Exception as e:
        print(f"Could not load model from {path}. Error: {e}")
        return None
