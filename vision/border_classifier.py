import cv2
import numpy as np


class BorderClassifier:

    def __init__(self, region):
        self.region = region

        self.svm = cv2.ml.SVM_create()
        self.svm.setType(cv2.ml.SVM_C_SVC)
        self.svm.setKernel(cv2.ml.SVM_LINEAR)
        self.svm.setC(1.0)

    def extract_features(self, image):
        x, y, w, h = self.region

        roi = image[y:y + h, x:x + w]
        rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)

        features = np.mean(rgb, axis=(0, 1)) / 255.0

        return features.astype(np.float32)

    def train(self, images, labels):
        features = np.array(
            [self.extract_features(image) for image in images],
            dtype=np.float32
        )

        labels = np.array(labels, dtype=np.int32)

        self.svm.train(
            features,
            cv2.ml.ROW_SAMPLE,
            labels
        )

    def predict(self, image):
        features = self.extract_features(image).reshape(1, -1)

        _, prediction = self.svm.predict(features)

        return bool(prediction[0, 0])