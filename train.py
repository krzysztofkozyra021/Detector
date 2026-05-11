import tensorflow as tf
import os
from model import create_model


def train_real_model(dataset_dir="polish-dataset", batch_size=32, epochs=10):
    train_dir = os.path.join(dataset_dir, "classification")
    if not os.path.exists(train_dir):
        print(f"Error: Could not find training directory at {train_dir}.")
        print(
            "Please ensure the dataset is extracted and 'classification' folder is present."
        )
        return
    print("Loading Polish Traffic Signs dataset...")
    train_dataset = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        labels="inferred",
        label_mode="int",
        color_mode="rgb",
        batch_size=batch_size,
        image_size=(64, 64),
        shuffle=True,
        validation_split=0.2,
        subset="training",
        seed=123,
    )
    val_dataset = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        labels="inferred",
        label_mode="int",
        color_mode="rgb",
        batch_size=batch_size,
        image_size=(64, 64),
        shuffle=True,
        validation_split=0.2,
        subset="validation",
        seed=123,
    )
    normalization_layer = tf.keras.layers.Rescaling(1.0 / 255)
    train_dataset = train_dataset.map(lambda x, y: (normalization_layer(x), y))
    val_dataset = val_dataset.map(lambda x, y: (normalization_layer(x), y))
    AUTOTUNE = tf.data.AUTOTUNE
    train_dataset = train_dataset.cache().prefetch(buffer_size=AUTOTUNE)
    val_dataset = val_dataset.cache().prefetch(buffer_size=AUTOTUNE)
    print("Creating model...")
    model = create_model(input_shape=(64, 64, 3), num_classes=21)
    print("Starting training...")
    model.fit(
        train_dataset,
        validation_data=val_dataset,
        epochs=epochs,
    )
    model.save("model.h5")
    print("Model trained and saved to model.h5 successfully!")


if __name__ == "__main__":
    train_real_model()
