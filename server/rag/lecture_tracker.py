import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict
from queue import Queue
from .rag import RAG
from config.config import Config

class LectureTracker:
    def __init__(self, rag_instance: RAG, 
                 buffer_size: int = Config.BUFFER_SIZE,
                 update_interval: int = Config.UPDATE_INTERVAL):
        self.rag_instance = rag_instance
        self.buffer_size = buffer_size
        self.update_interval = update_interval
        
        self.content_buffers: Dict[str, List[str]] = defaultdict(list)
        self.active_lectures: Dict[str, Dict] = {}
        self.processing_queue: Queue = Queue()
        
        self.chunk_counters: Dict[str, int] = defaultdict(int)
        self.last_processed: Dict[str, datetime] = {}
        self.lecture_metadata: Dict[str, Dict] = {}
        
        self.backup_content: Dict[str, List[Dict]] = defaultdict(list)
        self.error_logs: Dict[str, List[str]] = defaultdict(list)
        
        self._start_background_processors()

    def _generate_segment_id(self, session_key: str) -> str:
        return f"{session_key}_{str(uuid.uuid4())[:8]}"

    def _start_background_processors(self):
        update_thread = threading.Thread(
            target=self._periodic_update_worker,
            daemon=True
        )
        update_thread.start()
        
        process_thread = threading.Thread(
            target=self._process_queue_worker,
            daemon=True
        )
        process_thread.start()

    def add_or_update_lecture(self, course_title: str, lecture_title: str, 
                            content: str, segment_id: Optional[str] = None) -> dict:
        try:
            current_time = datetime.now()
            session_key = f"{course_title}_{lecture_title}_{current_time.date()}"
            
            if session_key not in self.active_lectures:
                self.active_lectures[session_key] = {
                    'course_title': course_title,
                    'lecture_title': lecture_title,
                    'start_time': current_time,
                    'last_update': current_time,
                    'status': 'active'
                }
            else:
                self.active_lectures[session_key]['last_update'] = current_time
            
            if not segment_id:
                segment_id = self._generate_segment_id(session_key)
            
            self.chunk_counters[session_key] += 1
            chunk_data = {
                'content': content,
                'timestamp': current_time.isoformat(),
                'chunk_number': self.chunk_counters[session_key],
                'segment_id': segment_id,
                'course_title': course_title,
                'lecture_title': lecture_title,
                'session_key': session_key
            }
            
            self.backup_content[session_key].append(chunk_data)
            if len(self.backup_content[session_key]) > 100:
                self.backup_content[session_key].pop(0)
            
            self.processing_queue.put(chunk_data)
            
            return {
                "status": "success",
                "session_key": session_key,
                "segment_id": segment_id,
                "chunk_number": self.chunk_counters[session_key]
            }
            
        except Exception as e:
            error_msg = f"Error adding lecture content: {str(e)}"
            self.error_logs[session_key].append(error_msg)
            return {"status": "error", "message": error_msg}

    def _process_queue_worker(self):
        while True:
            try:
                if not self.processing_queue.empty():
                    chunk_data = self.processing_queue.get()
                    self.rag_instance.add_lecture_chunk_to_db(chunk_data)
                    self.last_processed[chunk_data['session_key']] = datetime.now()
                time.sleep(1)
            except Exception as e:
                print(f"Error in queue processing: {str(e)}")

    def _periodic_update_worker(self):
        while True:
            try:
                current_time = datetime.now()
                for session_key, lecture_data in self.active_lectures.items():
                    if lecture_data['status'] != 'active':
                        continue
                        
                    last_processed = self.last_processed.get(session_key, datetime.min)
                    if (current_time - last_processed).seconds >= self.update_interval:
                        self._check_lecture_status(session_key, current_time)
                        
            except Exception as e:
                print(f"Error in periodic update: {str(e)}")
            time.sleep(self.update_interval)

    def _check_lecture_status(self, session_key: str, current_time: datetime):
        lecture_data = self.active_lectures[session_key]
        last_update = lecture_data['last_update']
        
        if (current_time - last_update).seconds > (self.update_interval * 2):
            lecture_data['status'] = 'inactive'
            lecture_data['end_time'] = current_time

    def get_lecture_status(self, course_title: str, lecture_title: str) -> dict:
        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"
        
        if session_key not in self.active_lectures:
            return {"status": "not_found"}
            
        lecture_data = self.active_lectures[session_key]
        return {
            "status": lecture_data['status'],
            "start_time": lecture_data['start_time'].isoformat(),
            "last_update": lecture_data['last_update'].isoformat(),
            "end_time": lecture_data.get('end_time', '').isoformat() if lecture_data.get('end_time') else None,
            "total_chunks": self.chunk_counters[session_key]
        }

    def recover_session(self, session_key: str) -> dict:
        try:
            if session_key not in self.backup_content:
                return {"status": "error", "message": "No backup found for session"}
                
            backup_chunks = self.backup_content[session_key]
            for chunk_data in backup_chunks:
                self.processing_queue.put(chunk_data)
                
            return {
                "status": "success",
                "message": f"Recovered {len(backup_chunks)} chunks",
                "recovered_chunks": len(backup_chunks)
            }
        except Exception as e:
            return {"status": "error", "message": f"Recovery failed: {str(e)}"}

    def finalize_lecture(self, course_title: str, lecture_title: str) -> dict:
        try:
            current_date = datetime.now().date()
            session_key = f"{course_title}_{lecture_title}_{current_date}"
            
            if session_key not in self.active_lectures:
                return {"status": "error", "message": "No active session found"}
                
            while not self.processing_queue.empty():
                time.sleep(1)
                
            self.active_lectures[session_key]['status'] = 'completed'
            self.active_lectures[session_key]['end_time'] = datetime.now()
            
            return {
                "status": "success",
                "message": "Lecture finalized successfully",
                "total_chunks": self.chunk_counters[session_key]
            }
        except Exception as e:
            error_msg = f"Failed to finalize lecture: {str(e)}"
            self.error_logs[session_key].append(error_msg)
            return {"status": "error", "message": error_msg}

    def get_error_logs(self, session_key: str) -> List[str]:
        return self.error_logs.get(session_key, [])

    def clear_error_logs(self, session_key: str) -> None:
        if session_key in self.error_logs:
            self.error_logs[session_key] = []

    def get_session_stats(self, session_key: str) -> dict:
        if session_key not in self.active_lectures:
            return {"status": "error", "message": "Session not found"}
            
        lecture_data = self.active_lectures[session_key]
        return {
            "status": lecture_data['status'],
            "start_time": lecture_data['start_time'].isoformat(),
            "last_update": lecture_data['last_update'].isoformat(),
            "end_time": lecture_data.get('end_time', '').isoformat() if lecture_data.get('end_time') else None,
            "total_chunks": self.chunk_counters[session_key],
            "processed_chunks": len(self.backup_content.get(session_key, [])),
            "pending_chunks": self.processing_queue.qsize(),
            "has_errors": bool(self.error_logs.get(session_key, []))
        }

    def cleanup_session(self, session_key: str) -> dict:
        try:
            if session_key not in self.active_lectures:
                return {"status": "error", "message": "Session not found"}
                
            if self.active_lectures[session_key]['status'] != 'completed':
                return {"status": "error", "message": "Cannot cleanup active session"}
                
            self.backup_content.pop(session_key, None)
            self.error_logs.pop(session_key, None)
            self.chunk_counters.pop(session_key, None)
            self.last_processed.pop(session_key, None)
            lecture_data = self.active_lectures.pop(session_key, None)
            
            return {
                "status": "success",
                "message": "Session cleaned up successfully",
                "session_data": lecture_data
            }
        except Exception as e:
            error_msg = f"Failed to cleanup session: {str(e)}"
            self.error_logs[session_key].append(error_msg)
            return {"status": "error", "message": error_msg}