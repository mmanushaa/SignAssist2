document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const inputText = document.getElementById('inputText');
    const convertTextBtn = document.getElementById('convertTextBtn');
    const recordVoiceBtn = document.getElementById('recordVoiceBtn');
    const stopRecordingBtn = document.getElementById('stopRecordingBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const results = document.getElementById('results');
    const noResults = document.getElementById('noResults');
    const originalText = document.getElementById('originalText');
    const islSentence = document.getElementById('islSentence');
    const detectedEmotion = document.getElementById('detectedEmotion');
    const videoContainer = document.getElementById('videoContainer');
    const noVideo = document.getElementById('noVideo');
    const signVideo = document.getElementById('signVideo');
    const playAllBtn = document.getElementById('playAllBtn');

    // MediaRecorder variables
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    // Video variables
    let videoPaths = [];
    let currentVideoIndex = 0;

    // Add event listeners
    convertTextBtn.addEventListener('click', processText);
    recordVoiceBtn.addEventListener('click', startRecording);
    stopRecordingBtn.addEventListener('click', stopRecording);
    playAllBtn.addEventListener('click', playAllVideos);
    signVideo.addEventListener('ended', playNextVideo);

    // Process text function
    function processText() {
        const text = inputText.value.trim();
        
        if (!text) {
            showAlert('Please enter some text first', 'warning');
            return;
        }
        
        // Show loading state
        convertTextBtn.disabled = true;
        convertTextBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        
        // Send request to server
        const formData = new FormData();
        formData.append('text', text);
        
        fetch('/process_text', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            displayResults(data, text);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('An error occurred while processing your text', 'danger');
        })
        .finally(() => {
            // Reset button state
            convertTextBtn.disabled = false;
            convertTextBtn.innerHTML = '<i class="fas fa-sign-language me-2"></i>Convert to Sign Language';
        });
    }

    // Start voice recording
    function startRecording() {
        if (isRecording) return;
        
        // Request microphone access
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                // Show recording UI
                recordVoiceBtn.classList.add('d-none');
                stopRecordingBtn.classList.remove('d-none');
                recordingStatus.classList.remove('d-none');
                
                // Initialize recorder
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                // Set up recorder events
                mediaRecorder.addEventListener('dataavailable', event => {
                    audioChunks.push(event.data);
                });
                
                mediaRecorder.addEventListener('stop', () => {
                    // Reset UI
                    recordVoiceBtn.classList.remove('d-none');
                    stopRecordingBtn.classList.add('d-none');
                    recordingStatus.classList.add('d-none');
                    
                    // Process recorded audio
                    processRecordedAudio();
                });
                
                // Start recording
                mediaRecorder.start();
                isRecording = true;
            })
            .catch(error => {
                console.error('Error accessing microphone:', error);
                showAlert('Unable to access microphone. Please check permissions.', 'danger');
            });
    }

    // Stop voice recording
    function stopRecording() {
        if (!isRecording || !mediaRecorder) return;
        
        mediaRecorder.stop();
        isRecording = false;
    }

    // Process recorded audio
    function processRecordedAudio() {
        // Create audio blob and form data
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob);
        
        // Show processing state
        recordingStatus.textContent = 'Processing audio...';
        recordingStatus.classList.remove('d-none');
        
        // Send to server
        fetch('/process_voice', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Server error');
            }
            return response.json();
        })
        .then(data => {
            // Update input text with transcribed speech
            inputText.value = data.text;
            
            // Display results
            displayResults(data, data.text);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('An error occurred while processing your speech', 'danger');
        })
        .finally(() => {
            recordingStatus.classList.add('d-none');
        });
    }

    // Display results
    function displayResults(data, originalTextValue) {
        // Show results section
        results.classList.remove('d-none');
        noResults.classList.add('d-none');
        
        // Update text fields
        originalText.textContent = originalTextValue;
        islSentence.textContent = data.isl_sentence;
        
        // Update emotion with icon
        const emotionIcons = {
            'happy': 'fa-smile',
            'sad': 'fa-frown',
            'angry': 'fa-angry',
            'surprise': 'fa-surprise',
            'fear': 'fa-meh-rolling-eyes',
            'disgust': 'fa-grimace',
            'neutral': 'fa-meh'
        };
        
        const emotionIcon = emotionIcons[data.emotion.toLowerCase()] || 'fa-meh';
        detectedEmotion.innerHTML = `<i class="far ${emotionIcon} me-2"></i>${data.emotion}`;
        
        // Handle videos
        if (data.video_paths && data.video_paths.length > 0) {
            videoPaths = data.video_paths;
            currentVideoIndex = 0;
            
            // Show video container
            videoContainer.classList.remove('d-none');
            noVideo.classList.add('d-none');
            
            // Load first video
            signVideo.src = videoPaths[0];
            signVideo.load();
        } else {
            // No videos available
            videoContainer.classList.add('d-none');
            noVideo.classList.remove('d-none');
        }
    }

    // Play all videos in sequence
    function playAllVideos() {
        currentVideoIndex = 0;
        signVideo.src = videoPaths[0];
        signVideo.load();
        signVideo.play()
            .catch(error => console.error('Error playing video:', error));
        
        // Update button
        playAllBtn.disabled = true;
        playAllBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Playing...';
    }

    // Play next video in sequence
    function playNextVideo() {
        currentVideoIndex++;
        
        if (currentVideoIndex < videoPaths.length) {
            // Play next video
            signVideo.src = videoPaths[currentVideoIndex];
            signVideo.load();
            signVideo.play()
                .catch(error => console.error('Error playing next video:', error));
        } else {
            // Reset to first video but don't play
            currentVideoIndex = 0;
            signVideo.src = videoPaths[0];
            signVideo.load();
            
            // Reset button
            playAllBtn.disabled = false;
            playAllBtn.innerHTML = '<i class="fas fa-play me-1"></i> Play All Signs';
        }
    }

    // Show alert message
    function showAlert(message, type) {
        // Create alert element
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert at top of card body
        const cardBody = document.querySelector('.card-body');
        cardBody.insertBefore(alertDiv, cardBody.firstChild);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => alertDiv.remove(), 150);
        }, 5000);
    }
});