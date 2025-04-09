import os
import uuid
import time
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from text_processor import TextProcessor
from sign_processor import SignLanguageProcessor
from moviepy import concatenate_videoclips, VideoFileClip

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/temp'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Ensure temp directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize processors
text_processor = TextProcessor()
sign_processor = SignLanguageProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/voice_to_sign')
def voice_to_sign():
    return render_template('text_to_isl.html')

@app.route('/sign_to_text')
def sign_to_text():
    return render_template('isl_to_text.html')

@app.route('/api/process_text', methods=['POST'])
def process_text():
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400

    preprocessed_text = text_processor.preprocess(text)
    emotion = text_processor.predict_emotion(preprocessed_text)
    video_paths = text_processor.find_video_paths(preprocessed_text)

    if not video_paths:
        return jsonify({"error": "No matching ISL videos found"}), 404

    # Create combined video
    clips = [VideoFileClip(path) for path in video_paths if os.path.exists(path)]
    if not clips:
        return jsonify({"error": "No valid video clips to combine"}), 500

    final_clip = concatenate_videoclips(clips)
    unique_id = str(uuid.uuid4())
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}.mp4")
    final_clip.write_videofile(output_path, codec="libx264", audio=False, logger=None)

    return jsonify({
        "success": True,
        "video_path": f"/static/temp/{unique_id}.mp4",
        "emotion": emotion,
        "text": text
    })

@app.route('/api/upload_sign_video', methods=['POST'])
def upload_sign_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400
    
    video_file = request.files['video']
    if video_file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(f"{uuid.uuid4()}.mp4")
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    video_file.save(filepath)

    try:
        sentence = sign_processor.predict_video(filepath)
        emotion = sign_processor.detect_emotion(filepath)

        return jsonify({
            "success": True,
            "predicted_text": sentence,
            "emotion": emotion
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_temp_files():
    now = time.time()
    count = 0
    for f in os.listdir(app.config['UPLOAD_FOLDER']):
        path = os.path.join(app.config['UPLOAD_FOLDER'], f)
        if os.path.isfile(path) and time.time() - os.path.getmtime(path) > 3600:
            os.remove(path)
            count += 1
    return jsonify({"success": True, "deleted_files": count})

if __name__ == '__main__':
    app.run(debug=True)
