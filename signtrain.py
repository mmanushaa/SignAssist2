import os
import re
import cv2
import numpy as np
import tensorflow as tf
from keras.api.models import Sequential
from keras.api.layers import LSTM, Dense, Dropout
from keras.api.callbacks import EarlyStopping, ReduceLROnPlateau
from keras.api.utils import to_categorical
import mediapipe as mp
import pickle
import random
from sklearn.model_selection import train_test_split

# Define constants
VIDEOS_FOLDER = r"vedios - Copy - Copy"
MODEL_DIR = r"models"
MAX_FRAMES = 30  # Number of frames per video

# Ensure model directory exists
os.makedirs(MODEL_DIR, exist_ok=True)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.5)

def extract_hand_features(frame, hands):
    """Extract hand landmarks using MediaPipe"""
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
    features = np.zeros((21, 3))
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        for i, landmark in enumerate(hand_landmarks.landmark):
            features[i] = [landmark.x, landmark.y, landmark.z]
    wrist_pos = features[0]
    features = features - wrist_pos
    return features.flatten()

def process_video(video_path, hands, max_frames=MAX_FRAMES):
    cap = cv2.VideoCapture(video_path)
    frames_features = []
    while len(frames_features) < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        features = extract_hand_features(frame, hands)
        frames_features.append(features)
    cap.release()
    if len(frames_features) < max_frames:
        padding = [np.zeros_like(frames_features[0]) for _ in range(max_frames - len(frames_features))]
        frames_features.extend(padding)
    elif len(frames_features) > max_frames:
        frames_features = frames_features[:max_frames]
    return np.array(frames_features)

def augment_sequence(sequence, num_augmentations=5):
    augmented_sequences = [sequence]
    for _ in range(num_augmentations):
        augmented = sequence.copy()
        if random.random() > 0.5:
            noise = np.random.normal(0, 0.02, augmented.shape)
            augmented += noise
        if random.random() > 0.5:
            scale_factor = random.uniform(0.9, 1.1)
            augmented *= scale_factor
        if random.random() > 0.7:
            landmarks = augmented.reshape(MAX_FRAMES, 21, 3)
            landmarks[:, :, 0] = -landmarks[:, :, 0]
            augmented = landmarks.reshape(MAX_FRAMES, 21 * 3)
        if random.random() > 0.6:
            frames = augmented.shape[0]
            if random.random() > 0.5 and frames > 5:
                to_remove = random.randint(1, min(5, frames // 4))
                indices_to_remove = random.sample(range(frames), to_remove)
                mask = np.ones(frames, dtype=bool)
                mask[indices_to_remove] = False
                augmented = augmented[mask]
                padding = np.zeros((to_remove, augmented.shape[1]))
                augmented = np.vstack([augmented, padding])
        augmented_sequences.append(augmented)
    return augmented_sequences

def extract_base_word(filename):
    """Removes trailing digits and separators to find base word"""
    base = os.path.splitext(filename)[0]
    return re.sub(r'[_\-\s]?\d+$', '', base)

def build_word_mapping(data_dir):
    """Creates mapping from video filename to base word"""
    word_mapping = {}
    for filename in os.listdir(data_dir):
        if filename.lower().endswith(('.mp4', '.mov')):
            word = extract_base_word(filename)
            word_mapping[filename] = word
    print(f"\n Found {len(word_mapping)} videos across {len(set(word_mapping.values()))} unique words: {sorted(set(word_mapping.values()))}")
    return word_mapping

def prepare_training_data(videos_folder, hands, max_frames=MAX_FRAMES, augment=True):
    X, y = [], []
    word_mapping = build_word_mapping(videos_folder)
    unique_words = sorted(set(word_mapping.values()))
    word_to_index = {word: i for i, word in enumerate(unique_words)}
    for filename, word in word_mapping.items():
        video_path = os.path.join(videos_folder, filename)
        try:
            features = process_video(video_path, hands, max_frames)
            label = word_to_index[word]
            if augment:
                augmented_sequences = augment_sequence(features, num_augmentations=9)
                for seq in augmented_sequences:
                    X.append(seq)
                    y.append(label)
            else:
                X.append(features)
                y.append(label)
        except Exception as e:
            print(f"⚠️ Error processing {filename}: {e}")
    X = np.array(X)
    y = to_categorical(y, num_classes=len(unique_words))
    print(f"\n Training data prepared: X shape {X.shape}, y shape {y.shape}")
    index_to_word = {i: word for word, i in word_to_index.items()}
    return X, y, word_to_index, index_to_word

def build_model(input_shape, num_classes):
    model = Sequential([
        LSTM(64, return_sequences=True, activation='tanh', input_shape=input_shape),
        Dropout(0.4),
        LSTM(32, activation='tanh'),
        Dropout(0.5),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    return model

def train_model(X, y, input_shape, num_classes, epochs=20, batch_size=4):
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    model = build_model(input_shape, num_classes)
    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=0.0001)
    ]
    model.fit(X_train, y_train, validation_data=(X_val, y_val),
              epochs=epochs, batch_size=batch_size, callbacks=callbacks, verbose=1)
    return model

# Main Training Block
try:
    X, y, word_to_index, index_to_word = prepare_training_data(VIDEOS_FOLDER, hands, augment=True)
    input_shape = (X.shape[1], X.shape[2])
    num_classes = len(word_to_index)
    model = train_model(X, y, input_shape, num_classes, epochs=20, batch_size=4)

    # Save model
    model_path = os.path.join(MODEL_DIR, "sign_language_model.h5")
    model.save(model_path)

    # Save metadata
    metadata = {
        "word_to_index": word_to_index,
        "index_to_word": index_to_word,
        "max_frames": MAX_FRAMES,
    }
    metadata_path = os.path.join(MODEL_DIR, "metadata.pkl")
    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)

    print(f"\n Training complete! Model saved at: {model_path}")
    print(f" Metadata saved at: {metadata_path}")

except Exception as e:
    print(f" Error during training: {e}")

finally:
    hands.close()

