from rag.lecture_rag import RAG

class QueryHandler:
    def __init__(self):
        self.rag = RAG()
        self.lecture_tracker = None

    def set_lecture_tracker(self, tracker):
        self.lecture_tracker = tracker

    def handle_query(self, course_title: str, lecture_title: str, question: str, prefer_recent: bool = True):
        """Process and handle a user query with preference for recent content."""
        try:
            if not question:
                return {"error": "Question cannot be empty"}

            # Get any in-memory content from current lecture
            in_memory_content = self.lecture_tracker.get_lecture_content(course_title, lecture_title) if self.lecture_tracker else ""
            
            # Query the RAG system with preference for recent content
            db_result = self.rag.query(question, prefer_recent=prefer_recent)

            if "error" in db_result:
                return db_result

            if db_result.get("from_gpt", False):
                # If it's a GPT response, return it directly
                return {
                    "answer": db_result["answer"],
                    "from_gpt": True,
                    "message": "This topic wasn't covered in the lecture, but here's a general answer:"
                }

            # Combine in-memory content with retrieved sources
            combined_sources = [in_memory_content] + db_result["sources"] if in_memory_content else db_result["sources"]
            
            response = {
                "answer": db_result["answer"],
                "sources": combined_sources,
                "titles": db_result["titles"],
                "from_recent": db_result.get("from_recent", False),
                "from_gpt": False
            }

            # Add context about recency if available
            if db_result.get("from_recent", False):
                response["context"] = "This was just discussed in the lecture."
            
            return response

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