from rag.lecture_rag import RAG

class QueryHandler():
    def __init__(self):
        self.rag = RAG()
        self.lecture_tracker = None

    def set_lecture_tracker(self, tracker):
        self.lecture_tracker = tracker

    def handle_query(self, course_title: str, lecture_title: str, question: str):
        """Process and handle a user query."""
        try:
            if not question:
                return {"error": "Question cannot be empty"}

            # Combine in-memory and database query logic here if needed
            in_memory_content = self.lecture_tracker.get_lecture_content(course_title, lecture_title) if self.lecture_tracker else ""
            db_result = self.rag.query(question)

            if db_result:
                combined_sources = [in_memory_content] + db_result["sources"] if in_memory_content else db_result["sources"]
                
                return {
                    "answer": db_result["answer"],
                    "sources": combined_sources,
                    "titles": db_result["titles"]
                }
            else:
                return {"error": "Failed to retrieve an answer"}
            
        except Exception as e:
            return {"error": f"An error occurred while processing the query: {str(e)}"}

    def add_lecture_to_db(self, course_title: str, lecture_title: str, content: str):
        """Add a lecture to the vector database."""
        try:
            if not course_title or not lecture_title or not content:
                return {"error": "All fields 'course_title', 'lecture_title', and 'content' are required"}

            success = self.rag.add_lecture_to_vector_db(course_title, lecture_title, content)

            if success:
                return {"message": f"Lecture '{lecture_title}' from course '{course_title}' added successfully"}
            else:
                return {"error": "Failed to add lecture to the database"}
            
        except Exception as e:
            return {"error": f"An error occurred while adding the lecture: {str(e)}"}