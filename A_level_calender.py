"""
Study Schedule Planner Application

This application helps students create study schedules based on their exam date,
available study time, and syllabus content. It collects user inputs, validates them,
and sends all information directly to Google Gemini AI to generate a study schedule.

Features:

- Console-based interface for easy interaction
- Input validation for dates and study hours
- Direct Google Gemini AI integration
- Automatic schedule generation based on collected data
  """

import json
import datetime
import os
from typing import Dict, Any, List

# =============================================================================

# CONFIGURATION - ADD YOUR GOOGLE GEMINI API KEY HERE

# =============================================================================

GEMINI_API_KEY = "AIzaSyA7XDQ4rXetbE0zXCWyK06z6d20UZGLTds"

# To get your API key:

# 1. Go to https://aistudio.google.com/app/apikey

# 2. Create a new API key

# 3. Replace “YOUR_GEMINI_API_KEY_HERE” with your actual key

# OR set as environment variable (recommended):

# export GEMINI_API_KEY=“your_actual_api_key_here”

# =============================================================================

class StudySchedulePlanner:
    """Main class for the study schedule planning application."""

    def __init__(self):
        self.exam_date = None
        self.study_hours_per_week = None
        self.syllabus_content = None
        self.request_data = {}
        self.api_key = GEMINI_API_KEY

    def validate_api_key(self) -> bool:
        """Validate that an API key has been configured."""
        # Check if API key is set in code or environment
        env_key = os.getenv("GEMINI_API_KEY")
        if self.api_key == "YOUR_GEMINI_API_KEY_HERE" and not env_key:
            print("❌ ERROR: Gemini API key not configured!")
            print("Please either:")
            print("1. Replace 'YOUR_GEMINI_API_KEY_HERE' in the code with your actual key")
            print("2. OR set environment variable: export GEMINI_API_KEY=\"your_key\"")
            print("Get your key from: https://aistudio.google.com/app/apikey")
            return False
        return True

    def get_exam_date(self) -> datetime.date:
        """Get and validate the exam date from user input."""
        while True:
            try:
                date_input = input("\nEnter your exam date (YYYY-MM-DD): ").strip()
                exam_date = datetime.datetime.strptime(date_input, "%Y-%m-%d").date()
                
                if exam_date <= datetime.date.today():
                    print("❌ Error: Exam date must be in the future. Please try again.")
                    continue
                
                if exam_date > datetime.date.today() + datetime.timedelta(days=365):
                    print("⚠️  Warning: Exam date is more than a year away.")
                    confirm = input("Continue with this date? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                return exam_date
                
            except ValueError:
                print("❌ Error: Invalid date format. Please use YYYY-MM-DD format.")

    def get_study_hours(self) -> float:
        """Get and validate the weekly study hours from user input."""
        while True:
            try:
                hours_input = input("\nEnter hours per week you can dedicate to study: ").strip()
                study_hours = float(hours_input)
                
                if study_hours <= 0:
                    print("❌ Error: Study hours must be a positive number.")
                    continue
                
                if study_hours > 168:
                    print("❌ Error: Cannot study more than 168 hours per week!")
                    continue
                
                if study_hours > 60:
                    print("⚠️  Warning: That's a lot of study hours per week!")
                    confirm = input("Continue with this amount? (y/n): ").strip().lower()
                    if confirm != 'y':
                        continue
                
                return study_hours
                
            except ValueError:
                print("❌ Error: Please enter a valid number for study hours.")

    def get_syllabus_content(self) -> str:
        """Get the syllabus content from user input."""
        print("\nEnter your complete syllabus content:")
        print("(Type your syllabus below. Press Enter twice when finished)")
        
        lines = []
        empty_line_count = 0
        
        while True:
            line = input()
            if line.strip() == "":
                empty_line_count += 1
                if empty_line_count >= 2:
                    break
            else:
                empty_line_count = 0
                lines.append(line)
        
        syllabus = "\n".join(lines).strip()
        
        if not syllabus:
            print("❌ Error: Syllabus cannot be empty!")
            return self.get_syllabus_content()
        
        return syllabus

    def collect_user_inputs(self) -> None:
        """Collect all required inputs from the user."""
        print("=" * 50)
        print("📚 STUDY SCHEDULE PLANNER")
        print("=" * 50)
        
        # Get exam date
        self.exam_date = self.get_exam_date()
        days_until_exam = (self.exam_date - datetime.date.today()).days
        print(f"✅ Exam date set: {self.exam_date} ({days_until_exam} days from today)")
        
        # Get study hours
        self.study_hours_per_week = self.get_study_hours()
        print(f"✅ Study hours per week: {self.study_hours_per_week}")
        
        # Get syllabus content
        self.syllabus_content = self.get_syllabus_content()
        print(f"✅ Syllabus content collected ({len(self.syllabus_content)} characters)")

    def create_request_object(self) -> Dict[str, Any]:
        """Create a structured request object with all user data."""
        days_until_exam = (self.exam_date - datetime.date.today()).days
        weeks_available = max(1, days_until_exam // 7)
        total_study_hours = self.study_hours_per_week * weeks_available
        
        request_data = {
            "exam_date": self.exam_date.isoformat(),
            "days_until_exam": days_until_exam,
            "weeks_available": weeks_available,
            "study_hours_per_week": self.study_hours_per_week,
            "total_study_hours_available": total_study_hours,
            "syllabus_content": self.syllabus_content,
            "request_timestamp": datetime.datetime.now().isoformat()
        }
        
        self.request_data = request_data
        return request_data

    def send_to_gemini_ai(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send all collected data directly to Google Gemini AI."""
        try:
            # Import the new Google AI library
            from google import genai
            
            # Configure the client with your API key
            client = genai.Client(api_key=self.api_key)
            
            # Create a simple prompt with all the collected information
            prompt = f"""

Create a detailed study schedule for a student with the following information:

Exam Date: {request_data['exam_date']}
Days until exam: {request_data['days_until_exam']} days
Study hours per week: {request_data['study_hours_per_week']} hours
Total weeks available: {request_data['weeks_available']} weeks
Total study hours available: {request_data['total_study_hours_available']} hours

Complete Syllabus:
{request_data['syllabus_content']}

Please create a week-by-week study plan with daily activities and provide study recommendations.
Format your response as a JSON object with this structure:
{{
“status”: “success”,
“schedule”: [
{{
“week_number”: 1,
“focus_topic”: “topic name”,
“daily_plan”: {{
“Monday”: “activity description”,
“Tuesday”: “activity description”,
“Wednesday”: “activity description”,
“Thursday”: “activity description”,
“Friday”: “activity description”,
“Saturday”: “activity description”,
“Sunday”: “activity description”
}}
}}
],
“recommendations”: [“tip1”, “tip2”, “tip3”]
}}
"""

            # Send to Gemma 3 E4B and get response
            response = client.models.generate_content(
                model='gemma-3-4b-it',
                contents=prompt
            )
            
            # Parse the response
            try:
                response_text = response.text.strip()
                # Remove code block markers if present
                if "```json" in response_text:
                    start = response_text.find("```json") + 7
                    end = response_text.rfind("```")
                    response_text = response_text[start:end].strip()
                elif "```" in response_text:
                    start = response_text.find("```") + 3
                    end = response_text.rfind("```")
                    response_text = response_text[start:end].strip()
                
                result = json.loads(response_text)
                return result
                
            except json.JSONDecodeError as e:
                return {
                    "status": "error", 
                    "error": f"Could not parse AI response: {str(e)}",
                    "raw_response": response.text[:500]
                }
            
        except ImportError:
            return {
                "status": "error", 
                "error": "Google AI library not installed. Run: pip install google-genai"
            }
        except Exception as e:
            return {"status": "error", "error": f"AI API Error: {str(e)}"}


    def display_schedule(self, schedule_response: Dict[str, Any]) -> None:
        """Display the generated study schedule."""
        if schedule_response.get("status") != "success":
            print("❌ Error generating schedule:", schedule_response.get("error", "Unknown error"))
            if "raw_response" in schedule_response:
                print("Raw AI response:", schedule_response["raw_response"])
            return
        
        print("\n" + "=" * 60)
        print("📅 YOUR AI-GENERATED STUDY SCHEDULE")
        print("=" * 60)
        print(f"🎯 Exam Date: {self.exam_date}")
        print(f"📚 Study Hours per Week: {self.study_hours_per_week}")
        
        print("\n📋 WEEKLY STUDY PLAN:")
        print("-" * 40)
        
        for week_data in schedule_response["schedule"]:
            print(f"\n🗓️  WEEK {week_data['week_number']}:")
            print(f"   📖 Focus: {week_data['focus_topic']}")
            
            print("   📅 Daily Plan:")
            for day, activity in week_data["daily_plan"].items():
                print(f"     {day:9}: {activity}")
        
        if "recommendations" in schedule_response:
            print(f"\n💡 AI RECOMMENDATIONS:")
            print("-" * 25)
            for i, rec in enumerate(schedule_response["recommendations"], 1):
                print(f"   {i}. {rec}")
        
        print(f"\n🎉 Good luck with your studies!")

    def save_schedule_to_file(self, schedule_response: Dict[str, Any]) -> None:
        """Save the schedule to a JSON file."""
        try:
            filename = f"study_schedule_{self.exam_date.strftime('%Y%m%d')}.json"
            
            complete_data = {
                "user_inputs": self.request_data,
                "ai_schedule": schedule_response,
                "generated_at": datetime.datetime.now().isoformat()
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(complete_data, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Schedule saved to: {filename}")
            
        except Exception as e:
            print(f"❌ Error saving schedule: {e}")

    def run(self) -> None:
        """Main application runner."""
        try:
            # Check API key
            if not self.validate_api_key():
                return
            
            # Collect all user inputs
            self.collect_user_inputs()
            
            # Package data
            print("\n🔄 Packaging your information...")
            request_data = self.create_request_object()
            
            # Send everything to Gemini AI
            print("🤖 Sending to Google Gemini AI...")
            print("⏳ Please wait while AI generates your schedule...")
            schedule_response = self.send_to_gemini_ai(request_data)
            
            # Show the results
            self.display_schedule(schedule_response)
            
            # Ask to save
            save_choice = input("\nSave this schedule to a file? (y/n): ").strip().lower()
            if save_choice == 'y':
                self.save_schedule_to_file(schedule_response)
            
            print("\n✨ Thank you for using Study Schedule Planner!")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")

def main():
    """Main entry point of the application."""
    planner = StudySchedulePlanner()
    planner.run()

if __name__ == "__main__":
    main()