from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import cv2
from object_detection1 import process_image  # Import the process_image function from object_detection.py

app = Flask(__name__)
CORS(app)  # Enable CORS if needed, especially useful during development and testing with front-end applications that might run on different servers.

@app.route('/upload', methods=['POST'])
def upload_image():
    # Ensure there is data in the request
    if not request.data:
        return jsonify({'error': 'No data provided'}), 400

    # Parse the JSON data
    data = request.get_json()

    # Ensure the 'image' key is in the data
    if 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    # Decode the image from base64
    try:
        image_data = data['image']
        image_decoded = base64.b64decode(image_data)
        image_np = np.frombuffer(image_decoded, dtype=np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({'error': 'Could not decode the image', 'details': str(e)}), 500

    # Process the image using the object detection module
    try:
        detected_objects = process_image(image)
    except Exception as e:
        return jsonify({'error': 'Error processing image', 'details': str(e)}), 500

    # Return the detection results
    return jsonify({
        'message': 'Image processed successfully',
        'objects': detected_objects
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
