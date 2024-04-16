import cv2
import base64

def image_to_base64(image_path):
    # Read the image using OpenCV
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("The image path is incorrect or the file is not accessible.")
    # Convert the image to PNG format to ensure format consistency
    _, image_encoded = cv2.imencode('.png', image)
    # Encode the converted image to base64
    image_base64 = base64.b64encode(image_encoded).decode('utf-8')
    return image_base64

# Specify the path to your image
image_path = '/Users/arturmuratov/PycharmProjects/cloud_ass1/inputfolder/000000012807.jpg'  # Change this to the path of your image file

# Convert the image and print the base64 string
base64_string = image_to_base64(image_path)
print(base64_string)
