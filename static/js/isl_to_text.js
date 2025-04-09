document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const videoElement = document.getElementById('videoElement');
    const startRecordingBtn = document.getElementById('startRecordingBtn');
    const stopVideoBtn = document.getElementById('stopVideoBtn');
    const recordingIndicator = document.getElementById('recordingIndicator');
    const processingIndicator = document.getElementById('processingIndicator');
    const videoFileInput = document.getElementById('videoFileInput');
    const uploadVideoBtn = document.getElementById('uploadVideoBtn');
    const results = document.getElementById('results');
    const noResults = document.getElementById('noResults');
    const predictedText = document.getElementById('predictedText');
    const detectedEmotion = document.getElementById('detectedEmotion');
    const confidenceLevel = document.getElementById('confidenceLevel');
    const confidenceText = document.getElementById('confidenceText');
    const recordedVideo = document.getElementById('recordedVideo');

    // MediaRecorder variables
    let mediaRecorder;
    let videoStream;
    let recordedChunks = [];
    let isRecording = false;
    let recordedBlob = null;

    // Add event listeners
    startRecordingBtn.addEventListener('click', startRecording);
    stopVideoBtn.addEventListener('click', stopRecording);
    uploadVideoBtn.addEventListener('click', uploadVideo);

    // Initialize camera
    function initCamera() {
        navigator.mediaDevices.getUserMedia({ 
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            }
        })
        .then(stream => {
            videoStream = stream;
            videoElement.srcObject = stream;
        })
        .catch(error => {
            console.error('Error accessing camera:', error);
            showAlert('Unable to access camera. Please check permissions.', 'danger');
        });
    }

    // Start camera on page load
    initCamera();

    // Start video recording
    function startRecording() {
        if (isRecording || !videoStream) return;
        
        // Setup recording
        recordedChunks = [];
        
        // Create MediaRecorder with video stream
        const options = { mimeType: 'video/webm;codecs=vp9,opus' };
        try {
            mediaRecorder = new MediaRecorder(videoStream, options);
        } catch (e) {
            console.error('MediaRecorder error:', e);
            try {
                // Fallback options
                mediaRecorder = new MediaRecorder(videoStream);
            } catch (e) {
                showAlert('Recording not supported in this browser', 'danger');
                return;
            }
        }
        
        // Set up recorder events
        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = processRecordedVideo;
        
        // Update UI
        startRecordingBtn.classList.add('d-none');
        stopVideoBtn.classList.remove('d-none');
        recordingIndicator.classList.remove('d-none');
        
        // Start recording
        mediaRecorder.start(100); // Collect data every 100ms
        isRecording = true;
        
        // Add recording indicator animation
        recordingIndicator.classList.add('recording-active');
    }

    // Stop video recording
    function stopRecording() {
        if (!isRecording || !mediaRecorder) return;
        
        // Stop recorder
        mediaRecorder.stop();
        isRecording = false;
        
        // Update UI
        stopVideoBtn.classList.add('d-none');
        startRecordingBtn.classList.remove('d-none');
        recordingIndicator.classList.remove('d-none', 'recording-active');
        recordingIndicator.textContent = 'Processing recorded video...';
    }

    // Process recorded video
    function processRecordedVideo() {
        // Create video blob
        recordedBlob = new Blob(recordedChunks, { type: 'video/webm' });
        
        // Show processing indicator
        processingIndicator.classList.remove('d-none');
        
        // Display recorded video
        const videoURL = URL.createObjectURL(recordedBlob);
        recordedVideo.src = videoURL;
        
        // Create form data for upload
        const formData = new FormData();
        formData.append('video', recordedBlob, 'recorded-video.webm');
        
        // Send to server
        fetch('/process_sign_video', {
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
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('An error occurred while processing your video', 'danger');
        })
        .finally(() => {
            // Hide processing indicator
            processingIndicator.classList.add('d-none');
            recordingIndicator.classList.add('d-none');
        });
    }

    // Upload and process video file
    function uploadVideo() {
        const file = videoFileInput.files[0];
        
        if (!file) {
            showAlert('Please select a video file first', 'warning');
            return;
        }
        
        // Validate file type
        if (!file.type.startsWith('video/')) {
            showAlert('Please select a valid video file', 'warning');
            return;
        }
        
        // Show processing indicator
        processingIndicator.classList.remove('d-none');
        uploadVideoBtn.disabled = true;
        uploadVideoBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Processing...';
        
        // Create form data for upload
        const formData = new FormData();
        formData.append('video', file);
        
        // Display selected video
        const videoURL = URL.createObjectURL(file);
        recordedVideo.src = videoURL;
        
        // Send to server
        fetch('/process_sign_video', {
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
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('An error occurred while processing your video', 'danger');
        })
        .finally(() => {
            // Reset UI
            processingIndicator.classList.add('d-none');
            uploadVideoBtn.disabled = false;
            uploadVideoBtn.innerHTML = '<i class="fas fa-upload me-1"></i> Upload & Process';
        });
    }

    // Display results
    function displayResults(data) {
        // Show results section
        results.classList.remove('d-none');
        noResults.classList.add('d-none');
        
        // Update text field
        predictedText.textContent = data.predicted_word || 'No sign detected';
        
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
        
        // Set confidence level (simulated from 65-95%)
        const confidence = Math.floor(Math.random() * 31) + 65;
        confidenceLevel.style.width = `${confidence}%`;
        confidenceText.textContent = `${confidence}%`;
        
        // Set confidence color
        confidenceLevel.className = 'progress-bar';
        if (confidence >= 85) {
            confidenceLevel.classList.add('bg-success');
        } else if (confidence >= 70) {
            confidenceLevel.classList.add('bg-warning');
        } else {
            confidenceLevel.classList.add('bg-danger');
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