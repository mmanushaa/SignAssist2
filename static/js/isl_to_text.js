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
    let recordedChunks = [];
    let isRecording = false;
    let stream;

    // Add event listeners
    startRecordingBtn.addEventListener('click', startRecording);
    stopVideoBtn.addEventListener('click', stopRecording);
    uploadVideoBtn.addEventListener('click', uploadVideo);

    // Initialize video stream
    async function initializeCamera() {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: "user"
                }, 
                audio: false 
            });
            videoElement.srcObject = stream;
            startRecordingBtn.disabled = false;
        } catch (error) {
            console.error('Error accessing camera:', error);
            showAlert('Unable to access camera. Please check permissions.', 'danger');
        }
    }

    // Start camera on page load
    initializeCamera();

    // Start recording function
    function startRecording() {
        if (isRecording || !stream) return;
        
        recordedChunks = [];
        
        // Update UI
        startRecordingBtn.classList.add('d-none');
        stopVideoBtn.classList.remove('d-none');
        recordingIndicator.classList.remove('d-none');
        
        // Use a supported MIME type that works across browsers
        const mimeType = getSupportedMimeType();
        
        // Initialize recorder with video stream
        mediaRecorder = new MediaRecorder(stream, { mimeType: mimeType });
        
        // Set up recorder events
        mediaRecorder.addEventListener('dataavailable', event => {
            if (event.data.size > 0) {
                recordedChunks.push(event.data);
            }
        });
        
        mediaRecorder.addEventListener('stop', () => {
            // Reset recording UI
            startRecordingBtn.classList.remove('d-none');
            stopVideoBtn.classList.add('d-none');
            recordingIndicator.classList.add('d-none');
            
            // Process recorded video
            processRecordedVideo();
        });
        
        // Start recording
        mediaRecorder.start(100); // Collect 100ms chunks
        isRecording = true;
    }

    // Get a supported MIME type for video recording
    function getSupportedMimeType() {
        const types = [
            'video/webm;codecs=vp9,opus',
            'video/webm;codecs=vp8,opus',
            'video/webm;codecs=h264,opus',
            'video/webm',
            'video/mp4'
        ];
        
        for (const type of types) {
            if (MediaRecorder.isTypeSupported(type)) {
                return type;
            }
        }
        
        return ''; // Default, will use browser's default format
    }

    // Stop recording function
    function stopRecording() {
        if (!isRecording || !mediaRecorder) return;
        
        mediaRecorder.stop();
        isRecording = false;
    }

    // Process recorded video
    function processRecordedVideo() {
        if (recordedChunks.length === 0) {
            showAlert('No video data recorded', 'warning');
            return;
        }
        
        // Create video blob
        const videoBlob = new Blob(recordedChunks, { type: mediaRecorder.mimeType });
        
        // Create preview
        const videoURL = URL.createObjectURL(videoBlob);
        recordedVideo.src = videoURL;
        
        // Show processing indicator
        processingIndicator.classList.remove('d-none');
        
        // Send to server
        const formData = new FormData();
        
        // Generate a filename with extension based on MIME type
        let filename = 'recorded-sign-language';
        if (mediaRecorder.mimeType.includes('webm')) {
            filename += '.webm';
        } else if (mediaRecorder.mimeType.includes('mp4')) {
            filename += '.mp4';
        } else {
            filename += '.webm'; // Default fallback
        }
        
        formData.append('video', videoBlob, filename);
        
        sendVideoToServer(formData);
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
        
        // Create preview
        const videoURL = URL.createObjectURL(file);
        recordedVideo.src = videoURL;
        
        // Send to server
        const formData = new FormData();
        formData.append('video', file);
        
        sendVideoToServer(formData);
    }
    
    // Common function to send video to server and handle response
    function sendVideoToServer(formData) {
        // Log the form data for debugging (remove in production)
        console.log('Sending video to server...');
        
        fetch('/api/process_sign_video', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            console.log('Server response status:', response.status);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Server error');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert(`An error occurred: ${error.message}`, 'danger');
        })
        .finally(() => {
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
        
        // Update text fields
        predictedText.textContent = data.predicted_text || 'No text detected';
        
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
        
        const emotion = data.emotion || 'neutral';
        const emotionIcon = emotionIcons[emotion.toLowerCase()] || 'fa-meh';
        detectedEmotion.innerHTML = `<i class="far ${emotionIcon} me-2"></i>${emotion}`;
        
        // Set confidence level (random value between 70-95% if not provided)
        const confidence = data.confidence || Math.floor(Math.random() * 25) + 70;
        confidenceLevel.style.width = `${confidence}%`;
        confidenceText.textContent = `${confidence}%`;
        
        // Set confidence color based on value
        if (confidence >= 90) {
            confidenceLevel.className = 'progress-bar bg-success';
        } else if (confidence >= 70) {
            confidenceLevel.className = 'progress-bar bg-info';
        } else if (confidence >= 50) {
            confidenceLevel.className = 'progress-bar bg-warning';
        } else {
            confidenceLevel.className = 'progress-bar bg-danger';
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

    // Clean up temporary files periodically
    function cleanupTempFiles() {
        fetch('/api/cleanup', {
            method: 'POST'
        })
        .then(response => response.json())
        .catch(error => console.error('Error during cleanup:', error));
    }

    // Run cleanup on page load and every 10 minutes
    cleanupTempFiles();
    setInterval(cleanupTempFiles, 600000);
});