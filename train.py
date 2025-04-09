import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
file_path = 'C:\\xampp\\htdocs\\English2ISLGenerator\\balanced_emotions.csv'
df = pd.read_csv(file_path, encoding='utf-8')

# Check for missing values
df.dropna(inplace=True)

# Encode labels
label_encoder = LabelEncoder()
df['label'] = label_encoder.fit_transform(df['label'])

# Preprocess and transform text using TF-IDF
vectorizer = TfidfVectorizer(max_features=5000, stop_words='english')
X = vectorizer.fit_transform(df['text'])
y = df['label']

# Train-test split (Stratified to balance classes)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Train SVM classifier using SGD (Faster)
model = SGDClassifier(loss='hinge', alpha=0.0001, max_iter=1000, random_state=42)
model.fit(X_train, y_train)

# Predict and evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=label_encoder.classes_))

# Save model, vectorizer, and encoder
joblib.dump(model, 'emotion_model_svm.pkl')
joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
joblib.dump(label_encoder, 'label_encoder.pkl')

# Function to predict emotion
def predict_emotion(text, model_path='emotion_model_svm.pkl', vectorizer_path='tfidf_vectorizer.pkl', encoder_path='label_encoder.pkl'):
    # Load the saved models
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
    label_encoder = joblib.load(encoder_path)

    # Transform input text and predict
    text_vectorized = vectorizer.transform([text])
    prediction = model.predict(text_vectorized)
    return label_encoder.inverse_transform(prediction)[0]

# Example usage
sentence = "I'm feeling really happy today!"
predicted_emotion = predict_emotion(sentence)
print(f"Predicted emotion: {predicted_emotion}")
