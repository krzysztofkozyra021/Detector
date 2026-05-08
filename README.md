# Traffic Sign Detector (MVP)

A web application based on a Convolutional Neural Network (CNN) model using TensorFlow/Keras for automatic recognition of traffic signs from the Polish Traffic Signs dataset (21 classes).

## Requirements and Technology
The project has been implemented as a simple MVP (Minimum Viable Product).
- **Technology:** Python, Flask, TensorFlow/Keras, OpenCV.
- **Interface:** A minimal web application that accepts images and displays the result.
- **Model:** The architecture expects RGB images of size `64x64`. The model needs to be trained on the Polish Traffic Signs dataset.
- **Formats:** Supported formats are PNG, JPG, and WebP.

## Running the Project

1. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Download the Polish Traffic Signs dataset and train the model. The application requires a `model.h5` file.
   To do this, download and extract the dataset directly from Kaggle:
   ```bash
   # 1. Download the dataset
   curl -L -o polish-traffic-signs-dataset.zip https://www.kaggle.com/api/v1/datasets/download/chriskjm/polish-traffic-signs-dataset
   
   # 2. Extract the downloaded archive into a newly created polish-dataset folder
   unzip polish-traffic-signs-dataset.zip -d polish-dataset
   
   # 3. Run the training script (it will automatically detect the polish-dataset/classification folder)
   python train.py
   ```

3. Run the web application:
   ```bash
   python app.py
   ```

4. Go to `http://127.0.0.1:5000` in your web browser.

## Performance Tests (Non-functional Requirements)
The project includes a script testing the inference time (required ≤ 500ms) and the repeatability of the results (required ≥ 95%).
Run the tests using the command:
   ```bash
   python test_performance.py
   ```

## Detection Algorithm Description
Since the dataset is primarily for classification (it contains already cropped signs), a heuristic detection module based on contours (OpenCV) was applied. It crops image fragments, filters out those smaller than the required resolution of 64x64 px, and then classifies them using the CNN model.
According to the MVP requirements:
1. Every sign in the image is detected and receives its `confidence score` (0-1).
2. If two speed limit signs are detected, the system gives priority to the closer sign (with a larger *bounding box* area) and discards the further one.
