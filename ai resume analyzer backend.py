from flask import Flask, request, jsonify
import pdfplumber
import openai
import logging
import os
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

# 🔹 Hardcode your OpenAI API key here
openai.api_key = "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"  # <-- Replace with your real API key

def extract_text_from_pdf(file_path):
    """ Extract text from PDF using pdfplumber """
    try:
        text = ""
        logging.debug(f"📂 Opening file: {file_path}")
        with pdfplumber.open(file_path) as pdf:  # Ensures the file is properly closed after reading
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        logging.info(f"✅ Extracted text length: {len(text)} characters")
        return text
    except Exception as e:
        logging.error(f"❌ Error extracting text: {e}")
        return None  # Return None if extraction fails

def analyze_resume_with_ai(resume_text):
    """ Use OpenAI API to analyze resume """
    try:
        prompt = f"""
        Analyze the following resume and provide structured feedback:
        
        1️⃣ **Key Skills Extracted**  
        2️⃣ **Relevant Experience**  
        3️⃣ **Education Summary**  
        4️⃣ **Strengths of the Resume**  
        5️⃣ **Weaknesses & Areas for Improvement**  
        6️⃣ **Missing Skills Compared to a Data Scientist Role**  
        7️⃣ **Job Match Score (Out of 100%)**  
        8️⃣ **Suggestions to Improve the Resume**  

        Resume Text:
        {resume_text}
        """

        logging.debug("🚀 Sending resume text to OpenAI API")
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response["choices"][0]["message"]["content"]
        logging.info("✅ AI analysis complete")
        return result
    except Exception as e:
        logging.error(f"❌ Error analyzing resume: {e}")
        return None  # Return None if OpenAI API fails

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    logging.debug("📩 Received a resume file for analysis.")
    
    if 'file' not in request.files:
        logging.error("❌ No file part in request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        logging.error("❌ No file selected.")
        return jsonify({"error": "No selected file"}), 400

    logging.info(f"📄 Processing file: {file.filename}")
    
    # Save file temporarily
    file_path = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(file_path)

    try:
        resume_text = extract_text_from_pdf(file_path)
        if not resume_text or resume_text.strip() == "":
            logging.error("❌ No text extracted from resume")
            return jsonify({"error": "Could not extract text from the resume. Please use a clear PDF."}), 400

        analysis_result = analyze_resume_with_ai(resume_text)

        # ✅ Wait for a short time before deleting to avoid access errors
        time.sleep(1)  # Small delay to allow the system to release the file
        
        # ✅ Ensure the file is not in use before deletion
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info("🗑️ Temp file deleted successfully.")

        if analysis_result:
            return jsonify({"analysis": analysis_result})
        else:
            return jsonify({"error": "Error analyzing resume. OpenAI API issue."}), 500

    except Exception as e:
        logging.error(f"❌ Error during resume analysis: {str(e)}")
        return jsonify({"error": f"Error in analysis: {str(e)}"}), 500

if __name__ == '__main__':
    print("✅ Flask server is running on http://127.0.0.1:5000/")
    app.run(debug=True)
