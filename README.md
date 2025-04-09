# Sign Language Translator Application

A comprehensive application for bridging communication gaps between sign language users and others. This application provides translation between text/speech and Indian Sign Language (ISL), as well as sign language recognition with emotion detection.

## Features

- **Voice to Text Conversion**: Record speech and convert it to text
- **Text to Sign Language**: Convert text to Indian Sign Language videos
- **Sign Language to Text**: Record sign language videos and convert them to text
- **Emotion Recognition**: Detect emotions from both text and sign language videos

## Prerequisites

- Python 3.8 or higher
- Webcam for sign language recording
- Microphone for voice recording
- The required ISL videos in the data/isl_videos directory

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/sign-language-translator.git
   cd sign-language-translator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Download pre-trained models (not included in the repository due to size):
   - Place sign language model in: `models/sign_language_model.h5`
   - Place metadata file in: `models/metadata.pkl`
   - Place emotion models in: `models/emotion_model_svm.pkl`, `models/tfidf_vectorizer.pkl`, and `models/label_encoder.pkl`

4. Add ISL videos to `data/isl_videos/`. The videos should follow these naming conventions:
   - Word videos: `Word.mp4` (e.g., `Hello.mp4`, `Thank.mp4`)
   - Letter videos: `A.mp4`, `B.mp4`, etc.

## Usage

1. Start the application:
   ```
   python app.py
   ```

2. Open your browser and navigate to http://localhost:5000

3. Choose the desired functionality:
   - Text to Sign Language: Enter text or record voice to convert to ISL videos
   - Sign Language to Text: Record or upload sign language videos to convert to text

## Application Structure

```
sign_language_app/
│
├── models/                 # Pre-trained machine learning models
├── data/                   # ISL videos and other data files
├── static/                 # CSS, JavaScript, and other static assets
├── templates/              # HTML templates
├── app.py                  # Main Flask application
├── text_processor.py       # Text processing and emotion detection from text
├── sign_language_processor.py  # Sign language processing and recognition
└── requirements.txt        # Python dependencies
```

## Technologies Used

- **Backend**: Flask, TensorFlow, MediaPipe, DeepFace, NLTK
- **Frontend**: HTML, CSS, JavaScript, Bootstrap
- **Media Processing**: OpenCV, MoviePy, SpeechRecognition

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This application uses pre-trained models for sign language recognition and emotion detection
- Special thanks to the MediaPipe team for their hand tracking implementation
