import cv2
import numpy as np

# Detects the shiny summary screen star using HOG features and a linear SVM.
class StarClassifier:
    # Initializes the star region, HOG descriptor, and linear SVM.
    def __init__(self, region):
        self.region = region
        self.hog = cv2.HOGDescriptor(
            (32, 32),  # Window size
            (16, 16),  # Block size
            (8, 8),    # Block stride
            (8, 8),    # Cell size
            9          # Orientation bins
        )
        self.svm = cv2.ml.SVM_create()
        self.svm.setType(cv2.ml.SVM_C_SVC)
        self.svm.setKernel(cv2.ml.SVM_LINEAR)
        self.svm.setC(1.0)

    # Extracts HOG features from the grayscale star region.
    def extract_features(self, image):
        x, y, w, h = self.region
        roi = image[y:y + h, x:x + w]
        resized = cv2.resize(roi, (32, 32), interpolation=cv2.INTER_NEAREST)
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        features = self.hog.compute(gray)
        return features.flatten().astype(np.float32)

    # Trains the SVM using labeled normal and shiny star images.
    def train(self, images, labels):
        features = np.array(
            [self.extract_features(image) for image in images],
            dtype=np.float32
        )
        labels = np.array(labels, dtype=np.int32)
        self.svm.train(features, cv2.ml.ROW_SAMPLE, labels)

    # Predicts whether the shiny star is present.
    def predict(self, image):
        features = self.extract_features(image).reshape(1, -1)
        _, prediction = self.svm.predict(features)
        return bool(prediction[0, 0])