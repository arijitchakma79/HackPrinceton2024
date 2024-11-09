from rag.lecture_rag import RAG  

class QueryHandler:
    def __init__(self):
        
        self.rag = RAG()

    def handle_query(self, question: str):

        try:
            if not question:
                return {"error": "Question cannot be empty"}

            result = self.rag.query(question)

            if result:
                return {
                    "answer": result["answer"],
                    "sources": result["sources"],
                    "titles": result["titles"]
                }
            else:
                return {"error": "Failed to retrieve an answer"}
        
        except Exception as e:
            return {"error": f"An error occurred while processing the query: {str(e)}"}

    def add_lecture_to_db(self, course_title: str, lecture_title: str, content: str):

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
