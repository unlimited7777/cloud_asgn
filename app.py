from flask import Flask, request, jsonify
import base64
import numpy as np
import cv2
from flask_cors import CORS


app = Flask(__name__)
CORS(app)  # Allows all domains to access this API

# Configuration parameters
confthres = 0.3
nmsthres = 0.1

# Set paths for YOLO configuration and weights
labelsPath = "coco.names"
cfgpath = "yolov3-tiny.cfg"
wpath = "yolov3-tiny.weights"

def load_labels(labels_path):
    try:
        with open(labels_path, 'r') as file:
            labels = file.read().strip().split("\n")
        return labels
    except FileNotFoundError:
        print("Labels file not found.")
        return []

def load_model(config_path, weights_path):
    print("[INFO] loading YOLO from disk...")
    net = cv2.dnn.readNetFromDarknet(config_path, weights_path)
    return net

def do_prediction(image, net, labels):
    (H, W) = image.shape[:2]
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layerOutputs = net.forward(ln)

    boxes = []
    confidences = []
    classIDs = []
    for output in layerOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > confthres:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    idxs = cv2.dnn.NMSBoxes(boxes, confidences, confthres, nmsthres)
    results = []
    if len(idxs) > 0:
        for i in idxs.flatten():
            results.append({
                'label': labels[classIDs[i]],
                'accuracy': confidences[i],
                'rectangle': {
                    'height': boxes[i][3],
                    'left': boxes[i][0],
                    'top': boxes[i][1],
                    'width': boxes[i][2]
                }
            })
    return results

labels = load_labels(labelsPath)
net = load_model(cfgpath, wpath)

@app.route('/upload', methods=['POST'])
def upload_image():
    data = request.get_json(force=True)
    if not data or 'image' not in data:
        return jsonify({'error': 'No image provided'}), 400

    image_id = data.get('id', 'default_id')
    try:
        image_data = data['image']
        image_decoded = base64.b64decode(image_data)
        image_np = np.frombuffer(image_decoded, dtype=np.uint8)
        image = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
        if image is None:
            return jsonify({'error': 'Invalid image, could not decode'}), 400
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    except Exception as e:
        return jsonify({'error': 'Error processing image', 'details': str(e)}), 500

    detections = do_prediction(image, net, labels)
    return jsonify({
        'id': image_id,
        'objects': detections
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

