"""
Flask application for creating and managing AI-generated images using Leonardo.ai API.

This application allows users to:
1. Generate images using Leonardo.ai's Phoenix model
2. Select preferred images from the generated set
3. Download selected images and attempt to share them on Pinterest
"""

import os
import time
import json
import requests
from flask import Flask, render_template, request, jsonify, send_file, Response, make_response
from flask_cors import CORS
from dotenv import load_dotenv
from io import BytesIO

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key')
LEONARDO_API_KEY = os.getenv('LEONARDO_API_KEY')
PINTEREST_ACCESS_TOKEN = os.getenv('PINTEREST_ACCESS_TOKEN')
LEONARDO_API_URL = "https://cloud.leonardo.ai/api/rest/v1"
PINTEREST_API_URL = "https://api.pinterest.com/v5"

def create_pinterest_board(board_name="AI Generated Art"):
    """
    Create a new Pinterest board if none exists.
    
    Args:
        board_name (str): Name for the new board
        
    Returns:
        str: Board ID or None if creation failed
    """
    if not PINTEREST_ACCESS_TOKEN:
        print("Pinterest access token not configured")
        return None

    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # First check if board already exists
        boards_response = requests.get(
            f"{PINTEREST_API_URL}/boards",
            headers=headers
        )
        boards_response.raise_for_status()
        boards_data = boards_response.json()
        
        for board in boards_data.get('items', []):
            if board.get('name') == board_name:
                return board.get('id')
        
        # If board doesn't exist, create it
        board_data = {
            "name": board_name,
            "description": "Collection of AI-generated artwork",
            "privacy": "PUBLIC"
        }
        
        response = requests.post(
            f"{PINTEREST_API_URL}/boards",
            headers=headers,
            json=board_data
        )
        response.raise_for_status()
        return response.json().get('id')
        
    except requests.exceptions.RequestException as e:
        print(f"Error creating Pinterest board: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error response content: {e.response.text}")
        return None

def upload_to_pinterest(image_url, board_id=None, note="AI generated image"):
    """
    Upload an image to Pinterest.
    
    Args:
        image_url (str): The URL of the image to upload
        board_id (str): The Pinterest board ID to upload to
        note (str): Description for the pin
        
    Returns:
        dict: Response from Pinterest API or None if failed
    """
    if not PINTEREST_ACCESS_TOKEN:
        print("Pinterest access token not configured")
        return None

    headers = {
        "Authorization": f"Bearer {PINTEREST_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # If no board_id provided, create a new board or get existing one
        if not board_id:
            board_id = create_pinterest_board()
            if not board_id:
                print("Failed to get or create Pinterest board")
                return None

        # Create pin with the image
        pin_data = {
            "board_id": board_id,
            "media_source": {
                "source_type": "image_url",
                "url": image_url
            },
            "note": note
        }
        
        response = requests.post(
            f"{PINTEREST_API_URL}/pins",
            headers=headers,
            json=pin_data
        )
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"Error uploading to Pinterest: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error response content: {e.response.text}")
        return None

@app.route('/')
def index():
    """Render the main page of the application."""
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Error rendering index: {str(e)}")
        return str(e), 500

@app.route('/generate', methods=['POST'])
def generate_images():
    """Generate images using Leonardo.ai API."""
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
            
        print(f"Received generation request with prompt: {prompt}")
        result = generate_images_with_leonardo(prompt)
        
        if isinstance(result, dict) and result.get('status') == 'pending':
            return jsonify(result), 202  # Return 202 Accepted for pending status
        
        if not result:
            return jsonify({'error': 'Failed to generate images'}), 500
            
        return jsonify({'images': result})
        
    except Exception as e:
        print(f"Error in generate_images endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download-and-pin', methods=['POST'])
def download_and_pin():
    """Download selected image and attempt to upload it to Pinterest."""
    image_url = request.json.get('image_url')
    if not image_url:
        return jsonify({'error': 'No image URL provided'}), 400
        
    try:
        # Try to upload to Pinterest first
        pinterest_result = None
        if PINTEREST_ACCESS_TOKEN:
            pinterest_result = upload_to_pinterest(image_url)
            if pinterest_result:
                print("Successfully uploaded to Pinterest")
        
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Create a BytesIO object from the image data
        image_data = BytesIO(response.content)
        
        # Generate a filename based on the current timestamp
        filename = f"generated_image_{int(time.time())}.png"
        
        # Create response with the file
        response = make_response(send_file(
            image_data,
            mimetype='image/png',
            as_attachment=True,
            download_name=filename
        ))
        
        # Add Pinterest status header
        response.headers['X-Pinterest-Status'] = 'success' if pinterest_result else 'failed'
        
        return response
        
    except requests.exceptions.RequestException as e:
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            error_msg = f"{error_msg}: {e.response.text}"
        return jsonify({'error': f'Failed to process image: {error_msg}'}), 500

def generate_images_with_leonardo(prompt):
    """
    Generate images using Leonardo.ai API with the specified model.
    
    Args:
        prompt (str): The text prompt for image generation
        
    Returns:
        list: List of image URLs or None if generation failed
    """
    # Updated model ID and parameters as per the curl example
    model_id = "6b645e3a-d64f-4341-a6d8-7a3690fbf042"
    
    # Headers for Leonardo.ai API
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "authorization": f"Bearer {LEONARDO_API_KEY}"
    }
    
    # Create generation request with updated parameters
    generation_url = f"{LEONARDO_API_URL}/generations"
    generation_payload = {
        "modelId": model_id,
        "contrast": 3.5,
        "prompt": prompt,
        "num_images": 4,
        "width": 1024,
        "height": 1024,
        "ultra": True,
        "styleUUID": "111dc692-d470-4eec-b791-3475abac4c46",
        "enhancePrompt": True
    }
    
    try:
        print(f"Using API URL: {generation_url}")
        print(f"Using headers: {headers}")
        print(f"Using payload: {generation_payload}")
        
        # Request image generation
        response = requests.post(
            generation_url,
            headers=headers,
            json=generation_payload
        )
        print(f"Initial response status: {response.status_code}")
        print(f"Initial response content: {response.text}")
        
        response.raise_for_status()
        response_data = response.json()
        print(f"Response data: {response_data}")
        
        generation_id = response_data.get('sdGenerationJob', {}).get('generationId')
        
        if not generation_id:
            print("No generation ID received")
            return None
            
        print(f"Generation ID received: {generation_id}")
        
        # Poll for generation results
        max_attempts = 60
        for attempt in range(max_attempts):
            print(f"Polling attempt {attempt + 1}")
            time.sleep(5)
            
            status_response = requests.get(
                f"{LEONARDO_API_URL}/generations/{generation_id}",
                headers=headers
            )
            print(f"Status check response: {status_response.status_code}")
            
            status_response.raise_for_status()
            generation_data = json.loads(status_response.text)
            generations_by_pk = generation_data.get('generations_by_pk', {})
            status = generations_by_pk.get('status')
            print(f"Generation status: {status}")
            
            if status == 'COMPLETE':
                # Return the generated image URLs
                images = generations_by_pk.get('generated_images', [])
                image_urls = [image.get('url') for image in images if image.get('url')]
                print(f"Generated image URLs: {image_urls}")
                if image_urls:
                    return image_urls
            elif status in ['FAILED', 'DELETED']:
                print(f"Generation failed with status: {status}")
                return None
                
        print("Generation timed out - this is normal for ultra-quality images")
        return jsonify({'status': 'pending', 'message': 'Image generation is still in progress. Please try again in a few minutes.'})
        
    except requests.exceptions.RequestException as e:
        print(f"Error generating images: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Error response content: {e.response.text}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
