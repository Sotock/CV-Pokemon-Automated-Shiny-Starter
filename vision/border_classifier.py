import cv2
import numpy as np

# Classifies summary screen borders using mean RGB features and a linear SVM.
class BorderClassifier:
    # Initializes the border region and linear SVM.
    def __init__(self, region):
        self.region = region
        self.svm = cv2.ml.SVM_create()
        self.svm.setType(cv2.ml.SVM_C_SVC)
        self.svm.setKernel(cv2.ml.SVM_LINEAR)
        self.svm.setC(1.0)

    # Extracts normalized mean RGB features from the border region.
    def extract_features(self, image):
        x, y, w, h = self.region
        roi = image[y:y + h, x:x + w]
        rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
        features = np.mean(rgb, axis=(0, 1)) / 255.0
        return features.astype(np.float32)

    # Trains the SVM using labeled normal and shiny border images.
    def train(self, images, labels):
        features = np.array(
            [self.extract_features(image) for image in images],
            dtype=np.float32
        )
        labels = np.array(labels, dtype=np.int32)
        self.svm.train(features, cv2.ml.ROW_SAMPLE, labels)

    # Predicts whether the border corresponds to a shiny encounter.
    def predict(self, image):
        features = self.extract_features(image).reshape(1, -1)
        _, prediction = self.svm.predict(features)
        return bool(prediction[0, 0])