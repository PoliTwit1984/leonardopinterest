# AI Image Generator with Pinterest Integration

A web application that generates AI images using Leonardo.ai and provides options for local download and Pinterest sharing.

## Features

### Currently Available
- ✓ AI Image Generation using Leonardo.ai's Phoenix model
- ✓ Ultra-quality image generation (1024x1024)
- ✓ Multiple image generation per prompt
- ✓ Image selection interface
- ✓ Local image download
- ✓ Responsive web interface
- ✓ Real-time generation status updates

### Pending API Approval
- ⏳ Pinterest integration (awaiting official API key approval)
  - Board creation
  - Image pinning
  - Custom board selection

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables in `.env`:
   ```
   LEONARDO_API_KEY=your_leonardo_api_key
   SECRET_KEY=your_flask_secret_key
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Usage

1. Enter a descriptive prompt for the image you want to generate
2. Click "Generate Images" and wait for the generation to complete
3. Select the images you want to save
4. Click "Download" to save the images locally

## Pinterest Integration Status

Pinterest integration is currently pending API approval. Once approved, users will be able to:
- Automatically create an "AI Generated Art" board
- Pin generated images directly to Pinterest
- Include custom descriptions for pins

For now, the application gracefully falls back to local downloads when Pinterest sharing is attempted.

## Technical Details

- Backend: Flask (Python)
- Frontend: Vanilla JavaScript
- Image Generation: Leonardo.ai API
- Image Storage: Local download support
- Status: Production-ready for local usage

## Error Handling

The application includes robust error handling for:
- Invalid prompts
- Failed image generations
- Network issues
- API timeouts
- Pinterest API unavailability

## Development Status

See [functionality.md](functionality.md) for detailed feature tracking and [pinterest_debugging.md](pinterest_debugging.md) for Pinterest integration progress.

## Next Steps

1. Await Pinterest API approval
2. Implement Pinterest board selection
3. Add image description customization
4. Add batch upload functionality
5. Implement image editing capabilities

## Notes

- Ultra-quality image generation may take several minutes
- Pinterest integration will be enabled automatically once API access is approved
- All generated images are temporarily stored and should be downloaded if you want to keep them
