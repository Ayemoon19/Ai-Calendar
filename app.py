from flask import Flask, request, jsonify
# Import your class from the calendar file (filename must match here)
from A_level_calender import StudySchedulePlanner  
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return "Welcome to the Study Schedule Planner API!"

@app.route("/generate", methods=["POST"])
def generate_schedule():
    data = request.get_json()

    # Make sure the required keys are present
    required_keys = {"exam_date", "study_hours_per_week", "syllabus_content"}
    if not data or not required_keys.issubset(data.keys()):
        return jsonify({"error": "Missing required keys: exam_date, study_hours_per_week, syllabus_content"}), 400

    try:
        planner = StudySchedulePlanner()

        # Set attributes directly from JSON (skip interactive input)
        planner.exam_date = datetime.datetime.strptime(data["exam_date"], "%Y-%m-%d").date()
        planner.study_hours_per_week = float(data["study_hours_per_week"])
        planner.syllabus_content = data["syllabus_content"]

        # Create request object & send to AI
        request_obj = planner.create_request_object()
        schedule = planner.send_to_gemini_ai(request_obj)

        return jsonify(schedule)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)