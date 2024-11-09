import threading
import time
from datetime import datetime
from collections import defaultdict

class LectureTracker:
    def __init__(self):
        self.active_lectures = defaultdict(str)
        self.query_handler = None

    def set_query_handler(self, handler):
        self.query_handler = handler

    def add_or_update_lecture(self, course_title: str, lecture_title: str, content: str) -> str:
        """Append new content to an existing lecture session or create a new one."""
        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"
        
        # Append new content to the existing session
        self.active_lectures[session_key] += f" {content}".strip()
        
        return session_key

    def get_lecture_content(self, course_title: str, lecture_title: str) -> str:
        """Retrieve current content of an ongoing lecture session."""
        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"
        return self.active_lectures.get(session_key, "")

    def start_periodic_db_update(self, interval: int = 60):
        """Start a background thread to save content to the database every minute."""
        if not self.query_handler:
            raise RuntimeError("QueryHandler not set. Call set_query_handler first.")

        def save_periodically():
            while True:
                try:
                    for session_key, content in self.active_lectures.items():
                        course_title, lecture_title, _ = session_key.split('_')
                        self.query_handler.add_lecture_to_db(course_title, lecture_title, content)
                except Exception as e:
                    print(f"Error in periodic update: {str(e)}")
                time.sleep(interval)

        thread = threading.Thread(target=save_periodically, daemon=True)
        thread.start()

    def finalize_lecture(self, course_title: str, lecture_title: str):
        """Finalize and store the lecture in the database."""
        if not self.query_handler:
            return {"error": "QueryHandler not set. Cannot finalize lecture."}

        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"

        if session_key in self.active_lectures:
            content = self.active_lectures[session_key]
            result = self.query_handler.add_lecture_to_db(course_title, lecture_title, content)

            if "message" in result:
                del self.active_lectures[session_key]  # Remove the session after storing
                return {"message": f"Lecture '{lecture_title}' from course '{course_title}' finalized and added to database."}
            else:
                return {"error": "Failed to add lecture to the database."}
        else:
            return {"error": "No active session found for the given lecture."}