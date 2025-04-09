# import os
# import cv2
# import numpy as np
# import tensorflow as tf
# import mediapipe as mp
# import pickle
# import argparse
# from deepface import DeepFace
# import time
# import collections

# # Define paths
# MODEL_PATH = r"models\sign_language_model.h5"
# METADATA_PATH = r"models\metadata.pkl"
# MAX_FRAMES = 30  # Number of frames per video

# # Load model
# if not os.path.exists(MODEL_PATH):
#     raise FileNotFoundError(f" Model not found at {MODEL_PATH}")
# model = tf.keras.models.load_model(MODEL_PATH)

# # Load metadata
# if not os.path.exists(METADATA_PATH):
#     raise FileNotFoundError(f" Metadata file not found at {METADATA_PATH}")
# with open(METADATA_PATH, "rb") as f:
#     metadata = pickle.load(f)

# word_to_index = metadata["word_to_index"]
# index_to_word = metadata["index_to_word"]

# # Initialize MediaPipe Hands
# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

# # Emotion recognition function
# def detect_emotion(video_path):
#     cap = cv2.VideoCapture(video_path)
#     emotion_counts = collections.Counter()
    
#     start_time = time.time()
#     frame_count = 0
    
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         # Process every 5th frame for efficiency
#         if frame_count % 5 == 0:
#             try:
#                 result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
#                 if result:
#                     emotion = result[0]['dominant_emotion']
#                     emotion_counts[emotion] += 1
#             except:
#                 pass
        
#         frame_count += 1

#     cap.release()
    
#     # Get the most common emotion
#     dominant_emotion = emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral"
#     return dominant_emotion

# # Feature extraction for sign recognition
# def extract_hand_features(frame):
#     frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = hands.process(frame_rgb)

#     features = np.zeros((21, 3))
#     if results.multi_hand_landmarks:
#         for i, landmark in enumerate(results.multi_hand_landmarks[0].landmark):
#             features[i] = [landmark.x, landmark.y, landmark.z]

#     wrist_pos = features[0]  # Normalize relative to the wrist
#     features = features - wrist_pos
#     return features.flatten()

# # Process video for sign recognition
# def process_video(video_path):
#     cap = cv2.VideoCapture(video_path)
#     frames_features = []

#     while len(frames_features) < MAX_FRAMES:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         features = extract_hand_features(frame)
#         frames_features.append(features)

#     cap.release()

#     # Ensure sequence length consistency
#     if len(frames_features) < MAX_FRAMES:
#         padding = [np.zeros_like(frames_features[0]) for _ in range(MAX_FRAMES - len(frames_features))]
#         frames_features.extend(padding)
#     elif len(frames_features) > MAX_FRAMES:
#         frames_features = frames_features[:MAX_FRAMES]

#     return np.array(frames_features)

# # Predict sign word from video
# def predict_video(video_path):
#     try:
#         features = process_video(video_path)
#         features = np.expand_dims(features, axis=0)

#         predictions = model.predict(features)
#         predicted_index = np.argmax(predictions)
#         predicted_word = index_to_word[predicted_index]

#         return predicted_word
#     except Exception as e:
#         print(f" Error processing {video_path}: {e}")
#         return None

# # Main function to handle multiple videos
# def main():
#     parser = argparse.ArgumentParser(description="Sign Language & Emotion Recognition")
#     parser.add_argument("videos", nargs="+", help="Paths to video files")
#     args = parser.parse_args()

#     video_paths = args.videos
#     sentence = []
#     emotions = []

#     for video_path in video_paths:
#         if os.path.exists(video_path):
#             predicted_word = predict_video(video_path)
#             detected_emotion = detect_emotion(video_path)

#             if predicted_word:
#                 sentence.append(predicted_word)
#             emotions.append(detected_emotion)
#         else:
#             print(f" File not found: {video_path}")

#     # Combine words into a sentence
#     final_sentence = " ".join(sentence)
#     most_common_emotion = collections.Counter(emotions).most_common(1)[0][0] if emotions else "neutral"

#     print("\n🔹 **Final Prediction** 🔹")
#     print(f"Sentence: {final_sentence}")
#     print(f"Most Common Emotion: {most_common_emotion}")

# if __name__ == "__main__":
#     main()

import os
import cv2
import numpy as np
import tensorflow as tf
from keras.api.models import load_model
import mediapipe as mp
import pickle
import collections
from deepface import DeepFace

class SignLanguageProcessor:
    def __init__(self):
        self.model = load_model("models/sign_language_model.h5")
        with open("models/metadata.pkl", "rb") as f:
            meta = pickle.load(f)
        self.word_to_index = meta["word_to_index"]
        self.index_to_word = meta["index_to_word"]
        self.MAX_FRAMES = 30

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False, max_num_hands=2)

    def detect_emotion(self, video_path):
        cap = cv2.VideoCapture(video_path)
        emotion_counts = collections.Counter()
        i = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            if i % 5 == 0:
                try:
                    result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False, silent=True)
                    if result:
                        emotion_counts[result[0]['dominant_emotion']] += 1
                except:
                    pass
            i += 1
        cap.release()
        return emotion_counts.most_common(1)[0][0] if emotion_counts else "neutral"

    def extract_hand_features(self, frame):
        results = self.hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        features = np.zeros((21, 3))
        if results.multi_hand_landmarks:
            for i, lm in enumerate(results.multi_hand_landmarks[0].landmark):
                features[i] = [lm.x, lm.y, lm.z]
        features -= features[0]
        return features.flatten()

    def process_video(self, path):
        cap = cv2.VideoCapture(path)
        features = []
        while len(features) < self.MAX_FRAMES:
            ret, frame = cap.read()
            if not ret:
                break
            features.append(self.extract_hand_features(frame))
        cap.release()
        while len(features) < self.MAX_FRAMES:
            features.append(np.zeros_like(features[0]))
        return np.array(features[:self.MAX_FRAMES])

    def predict_video(self, path):
        features = self.process_video(path)
        features = np.expand_dims(features, axis=0)
        preds = self.model.predict(features)
        return self.index_to_word[np.argmax(preds)]
