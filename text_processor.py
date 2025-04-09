# import sys
# import nltk
# import joblib
# import argparse
# import re
# import warnings
# import os
# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer
# from sklearn.feature_extraction.text import TfidfVectorizer
# from moviepy import VideoFileClip, concatenate_videoclips
# import traceback

# # Suppress warnings
# warnings.filterwarnings("ignore")

# # Download required NLTK resources
# nltk.download("punkt", quiet=True)
# nltk.download("wordnet", quiet=True)
# nltk.download("stopwords", quiet=True)

# # Load trained models
# model = joblib.load("emotion_model_svm.pkl")
# vectorizer = joblib.load("tfidf_vectorizer.pkl")
# label_encoder = joblib.load("label_encoder.pkl")

# class TextPreprocessor:
#     def __init__(self):
#         self.lemmatizer = WordNetLemmatizer()
#         self.stop_words = set(stopwords.words("english")) - {"you", "i", "we", "he", "she"}

#     def preprocess(self, text):
#         if not isinstance(text, str) or not text.strip():
#             return ""
#         text = text.lower()
#         text = re.sub(r"[^a-zA-Z\s]", "", text)
#         tokens = text.split()
#         tokens = [self.lemmatizer.lemmatize(word) for word in tokens if word not in self.stop_words]
#         return " ".join(tokens)

# def predict_emotion(text):
#     if not text.strip():
#         return "Unknown"
#     text_vectorized = vectorizer.transform([text])
#     predicted_label = model.predict(text_vectorized)
#     return label_encoder.inverse_transform(predicted_label)[0]

# def preprocess_and_find_mp4(text, folder):
#     words = text.lower().split()
#     mp4_files = []
#     all_files = set(os.listdir(folder))

#     for word in words:
#         word_mp4 = f"{word.capitalize()}.mp4"
#         word_path = os.path.join(folder, word_mp4)

#         if word_mp4 in all_files:
#             mp4_files.append(word_path)
#         else:
#             for letter in word:
#                 letter_mp4 = f"{letter.upper()}.mp4"
#                 if letter_mp4 in all_files:
#                     mp4_files.append(os.path.join(folder, letter_mp4))
#                 else:
#                     print(f"Missing file for: {letter_mp4}")

#     return mp4_files

# def create_video_from_mp4(mp4_files, output_path):
#     if not mp4_files:
#         print("Error: No MP4 files provided")
#         return False

#     clips = []
#     try:
#         missing_files = [f for f in mp4_files if not os.path.exists(f)]
#         if missing_files:
#             print(f"Error: Missing files: {missing_files}")
#             return False

#         for mp4 in mp4_files:
#             try:
#                 clip = VideoFileClip(mp4)
#                 if clip.duration <= 0:
#                     print(f"Warning: Zero-length clip: {mp4}")
#                     clip.close()
#                     continue
#                 clips.append(clip.without_audio())
#             except Exception as e:
#                 print(f"Error loading {mp4}: {str(e)}")
#                 continue

#         if not clips:
#             print("Error: No valid clips could be loaded")
#             return False

#         final_clip = concatenate_videoclips(clips)
#         final_clip.write_videofile(
#             output_path,
#             fps=24,
#             codec="libx264",
#             threads=4,
#             preset='ultrafast',
#             ffmpeg_params=['-crf', '23']
#         )
#         return True

#     except Exception as e:
#         print(f"Video creation error: {str(e)}")
#         if "ffmpeg" in str(e).lower():
#             print("\nFFmpeg troubleshooting:")
#             print("1. Ensure FFmpeg is installed: https://ffmpeg.org/")
#             print("2. Try: pip install --upgrade imageio-ffmpeg")
#         return False
#     finally:
#         for clip in clips:
#             try:
#                 clip.close()
#             except:
#                 pass

# def main():
#     parser = argparse.ArgumentParser(description="ISL Sentence Generation & Emotion Prediction with Video Creation")
#     parser.add_argument("text", type=str, help="Text to process")
#     parser.add_argument("--folder", type=str, default="vedios - Copy - Copy copy", help="Folder containing mp4 files")
#     parser.add_argument("--output_video", type=str, help="Path for the output video (default: 'output.mp4')")

#     args = parser.parse_args()

#     # Always overwrite 'output.mp4' in the same directory
#     output_path = args.output_video if args.output_video else "output.mp4"

#     processor = TextPreprocessor()
#     isl_sentence = processor.preprocess(args.text)
#     emotion = predict_emotion(args.text)

#     print("\nInput Text:", args.text)
#     print("ISL Sentence:", isl_sentence)
#     print("Predicted Emotion:", emotion)

#     mp4_files = preprocess_and_find_mp4(isl_sentence, args.folder)

#     if not mp4_files:
#         print("No matching videos found.")
#         return

#     success = create_video_from_mp4(mp4_files, output_path)
#     if success:
#         print(f"\n✅ Video created successfully at: {output_path}")
#     else:
#         print("\n❌ Video creation failed.")

# if __name__ == "__main__":
#     main()

import os
import re
import nltk
import joblib
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

nltk.download("punkt", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("stopwords", quiet=True)

class TextProcessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english")) - {"you", "i", "we", "he", "she"}

        self.model = joblib.load("emotion_model_svm.pkl")
        self.vectorizer = joblib.load("tfidf_vectorizer.pkl")
        self.label_encoder = joblib.load("label_encoder.pkl")
        self.videos_path = "vedios - Copy - Copy copy"

    def preprocess(self, text):
        if not isinstance(text, str) or not text.strip():
            return ""
        text = re.sub(r"[^a-zA-Z\s]", "", text.lower())
        tokens = text.split()
        tokens = [self.lemmatizer.lemmatize(w) for w in tokens if w not in self.stop_words]
        return " ".join(tokens)

    def predict_emotion(self, text):
        if not text:
            return "Unknown"
        vec = self.vectorizer.transform([text])
        pred = self.model.predict(vec)
        return self.label_encoder.inverse_transform(pred)[0]

    def find_video_paths(self, isl_sentence):
        words = isl_sentence.split()
        files = set(os.listdir(self.videos_path))
        video_paths = []

        for word in words:
            full_path = f"{word.capitalize()}.mp4"
            if full_path in files:
                video_paths.append(os.path.join(self.videos_path, full_path))
            else:
                for ch in word:
                    ch_path = f"{ch.upper()}.mp4"
                    if ch_path in files:
                        video_paths.append(os.path.join(self.videos_path, ch_path))
        return video_paths
