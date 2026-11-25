import cv2

print("Location:", getattr(cv2, "__file__", "Unknown"))
print("Version:", getattr(cv2, "__version__", "Unknown"))
print("ML available:", hasattr(cv2, "ml"))
print("HOG available:", hasattr(cv2, "HOGDescriptor"))