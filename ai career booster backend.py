from flask import Flask, request, jsonify
import openai

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# OpenAI API Key (Replace with your actual key)
OPENAI_API_KEY = "your_openai_api_key"
openai.api_key = OPENAI_API_KEY

print("🚀 Flask server is starting...")  # Debugging line

# Sample career paths database (you can expand this)
career_paths = {
    "Software Engineer": {
        "next_roles": ["Senior Software Engineer", "Tech Lead", "Engineering Manager"],
        "skills_required": ["System Design", "Cloud Computing", "Machine Learning"],
        "resources": [
            {"name": "System Design Course", "link": "https://systemdesign.com"},
            {"name": "AWS Certification", "link": "https://aws.amazon.com/certification/"}
        ],
        "side_projects": [
            "Build an open-source project",
            "Develop a personal portfolio website"
        ]
    },

    "Data Scientist": {
        "next_roles": ["Senior Data Scientist", "AI Engineer", "Chief Data Officer"],
        "skills_required": ["Deep Learning", "Big Data Analytics", "MLOps"],
        "resources": [
            {"name": "Deep Learning Course", "link": "https://deeplearning.ai"},
            {"name": "Big Data Specialization", "link": "https://coursera.org"}
        ],
        "side_projects": [
            "Create a stock price predictor",
            "Build a recommendation system"
        ]
    }
}

# AI-based prediction function
def generate_future_path(user_input):
    prompt = f"User wants to be a {user_input['career_goal']} and has skills: {', '.join(user_input['skills'])}. Suggest next job roles, missing skills, and a learning plan."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]

@app.route('/')
def home():
    return "Flask backend is running!"

@app.route('/predict_career', methods=['POST'])
def predict_career():
    print("📩 Received a career prediction request")  # Debugging line
    data = request.json
    career_goal = data.get("career_goal", "").title()
    skills = data.get("skills", [])

    if career_goal in career_paths:
        career_info = career_paths[career_goal]
        return jsonify({
            "next_roles": career_info["next_roles"],
            "missing_skills": [skill for skill in career_info["skills_required"] if skill not in skills],
            "learning_resources": career_info["resources"],
            "side_projects": career_info["side_projects"]
        })
    else:
        # Use AI to predict if career is not in the database
        ai_generated_path = generate_future_path(data)
        return jsonify({"ai_suggested_path": ai_generated_path})

if __name__ == '__main__':
    print("✅ Flask server is running on http://127.0.0.1:5000/")
    app.run(debug=True)
