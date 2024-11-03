// Main JavaScript functionality
console.log('Main.js loaded');

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    
    // Get form elements
    const generateForm = document.getElementById('generateForm');
    const promptInput = document.getElementById('prompt');
    const imageGrid = document.getElementById('imageGrid');
    const selectedSection = document.querySelector('.selected-section');
    const selectedImages = document.getElementById('selectedImages');
    const downloadBtn = document.getElementById('downloadBtn');

    let selectedImageUrls = new Set();

    // Form submission handler
    generateForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        // Get prompt value
        const promptValue = promptInput.value;
        console.log('Submitting form with prompt:', promptValue);
        
        if (!promptValue || promptValue.trim() === '') {
            console.log('Empty prompt detected');
            alert('Please enter a prompt');
            promptInput.focus();
            return;
        }

        // Show loading state
        imageGrid.innerHTML = '<div class="loading">Generating ultra-quality images. This may take several minutes...</div>';
        
        try {
            console.log('Sending generation request...');
            const response = await fetch('/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: promptValue.trim() }),
            });
            
            console.log('Generation response status:', response.status);
            
            if (!response.ok && response.status !== 202) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Generation response data:', data);
            
            if (data.error) {
                throw new Error(data.error);
            }

            // Handle pending status
            if (data.status === 'pending') {
                imageGrid.innerHTML = `
                    <div class="pending-message">
                        <p>${data.message}</p>
                        <button onclick="window.location.reload()">Check Again</button>
                    </div>
                `;
                return;
            }
            
            // Clear previous selections
            selectedImageUrls.clear();
            selectedSection.classList.add('hidden');
            
            // Display the generated images
            if (Array.isArray(data.images) && data.images.length > 0) {
                console.log('Displaying generated images:', data.images.length);
                imageGrid.innerHTML = data.images.map(imageUrl => `
                    <div class="image-card" onclick="window.toggleImageSelection('${imageUrl}', this)">
                        <img src="${imageUrl}" alt="Generated image">
                    </div>
                `).join('');
            } else {
                throw new Error('No images were generated');
            }
            
        } catch (error) {
            console.error('Error in image generation:', error);
            imageGrid.innerHTML = `<p class="error">Error: ${error.message}</p>`;
        }
    });

    // Image selection handler
    window.toggleImageSelection = function(imageUrl, element) {
        console.log('Toggling image selection:', imageUrl);
        
        if (selectedImageUrls.has(imageUrl)) {
            selectedImageUrls.delete(imageUrl);
            element.classList.remove('selected');
        } else {
            selectedImageUrls.add(imageUrl);
            element.classList.add('selected');
        }

        // Show/hide selected section based on whether any images are selected
        selectedSection.classList.toggle('hidden', selectedImageUrls.size === 0);
        updateSelectedImagesDisplay();
    };

    // Update selected images display
    function updateSelectedImagesDisplay() {
        selectedImages.innerHTML = Array.from(selectedImageUrls)
            .map(url => `
                <div class="image-card">
                    <img src="${url}" alt="Selected image">
                </div>
            `).join('');
    }

    // Download and Pinterest upload handler
    downloadBtn.addEventListener('click', async () => {
        if (selectedImageUrls.size === 0) {
            alert('Please select at least one image to download');
            return;
        }

        try {
            for (const imageUrl of selectedImageUrls) {
                // Show loading state
                const loadingMessage = document.createElement('div');
                loadingMessage.className = 'loading-message';
                loadingMessage.textContent = 'Processing image...';
                document.body.appendChild(loadingMessage);

                console.log('Processing image:', imageUrl);
                const response = await fetch('/download-and-pin', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ image_url: imageUrl }),
                });
                
                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.error || 'Failed to process image');
                }
                
                // Get Pinterest upload status
                const pinterestStatus = response.headers.get('X-Pinterest-Status');
                console.log('Pinterest upload status:', pinterestStatus);
                
                // Create a temporary link to trigger the download
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = response.headers.get('content-disposition')?.split('filename=')[1] || 'generated_image.png';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);

                // Remove loading message
                document.body.removeChild(loadingMessage);

                // Show appropriate status message
                const statusMessage = document.createElement('div');
                statusMessage.className = `status-message ${pinterestStatus === 'success' ? 'success' : ''}`;
                statusMessage.textContent = pinterestStatus === 'success' 
                    ? 'Image downloaded and shared on Pinterest!'
                    : 'Image downloaded successfully (Pinterest sharing unavailable)';
                document.body.appendChild(statusMessage);
                
                // Remove status message after 3 seconds
                setTimeout(() => {
                    document.body.removeChild(statusMessage);
                }, 3000);
            }

            // Clear selections after successful processing
            selectedImageUrls.clear();
            selectedSection.classList.add('hidden');
            updateSelectedImagesDisplay();

        } catch (error) {
            console.error('Error processing images:', error);
            alert(`Failed to process images: ${error.message}`);
        }
    });

    console.log('All event listeners attached');
});
