import threading
import time
from datetime import datetime
from typing import Dict
from rag.rag import RAG

class LectureTracker:
    def __init__(self, rag_instance: RAG, update_interval: int = 60):
        self.rag_instance = rag_instance
        self.active_lectures: Dict[str, str] = {}
        self.update_interval = update_interval

    def add_or_update_lecture(self, course_title: str, lecture_title: str, content: str) -> str:
        
        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"

        if session_key in self.active_lectures:
            self.active_lectures[session_key] += f" {content}".strip()
        else:
            self.active_lectures[session_key] = content

        return session_key

    def get_lecture_content(self, course_title: str, lecture_title: str) -> str:
        
        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"
        return self.active_lectures.get(session_key, "")

    def start_periodic_db_update(self):
   
        def save_periodically():
            while True:
                try:
                    for session_key, content in self.active_lectures.items():
                        course_title, lecture_title, _ = session_key.split('_')
                        self.rag_instance.add_lecture_to_db(course_title, lecture_title, content)
                except Exception as e:
                    print(f"Error during periodic update: {str(e)}")
                time.sleep(self.update_interval)

        thread = threading.Thread(target=save_periodically, daemon=True)
        thread.start()

    def finalize_lecture(self, course_title: str, lecture_title: str) -> dict:

        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"

        if session_key in self.active_lectures:
            content = self.active_lectures.pop(session_key)
            result = self.rag_instance.add_lecture_to_db(course_title, lecture_title, content)
            return {"status": "success", "message": f"Lecture '{lecture_title}' finalized."} if result['status'] == 'success' else {"status": "error", "message": result['message']}
        else:
            return {"status": "error", "message": "No active session found for the given lecture."}
