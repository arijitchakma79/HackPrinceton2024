from rag.rag import RAG
from rag.lecture_tracker import LectureTracker

rag_instance = RAG()
lecture_tracker = LectureTracker(rag_instance)

def add_lecture_handler(course_title: str, lecture_title: str, content: str) -> dict:
    return lecture_tracker.add_or_update_lecture(course_title, lecture_title, content)

def query_handler_function(question: str, course_title: str, lecture_title: str, 
                         segment_id: str = None, prefer_recent: bool = True, 
                         limit: int = 3) -> dict:
    return rag_instance.query(
        question, 
        course_title, 
        lecture_title, 
        segment_id=segment_id,
        prefer_recent=prefer_recent, 
        limit=limit
    )

def finalize_lecture_handler(course_title: str, lecture_title: str) -> dict:
    return lecture_tracker.finalize_lecture(course_title, lecture_title)

def get_lecture_status_handler(course_title: str, lecture_title: str) -> dict:
    return lecture_tracker.get_lecture_status(course_title, lecture_title)

def get_session_stats_handler(session_key: str) -> dict:
    return lecture_tracker.get_session_stats(session_key)

def cleanup_session_handler(session_key: str) -> dict:
    return lecture_tracker.cleanup_session(session_key)

def recover_session_handler(session_key: str) -> dict:
    return lecture_tracker.recover_session(session_key)

def get_complete_lecture_handler(course_title: str, lecture_title: str) -> dict:
    return rag_instance.get_complete_lecture(course_title, lecture_title)