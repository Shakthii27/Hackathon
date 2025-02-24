from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Load the trained AI model
MODEL_PATH = "ai_detector_model.h5"
model = load_model(MODEL_PATH)

def predict_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img) / 255.0  # Normalize
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    
    prediction = model.predict(img_array)
    return "Real" if prediction[0][0] > 0.5 else "AI Edited"

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"})
    
    file = request.files["file"]
    file_path = "uploaded_image.jpg"
    file.save(file_path)
    
    result = predict_image(file_path)
    os.remove(file_path)  # Clean up uploaded file
    
    return jsonify({"prediction": result})

if __name__ == "__main__":
    app.run(debug=True)
