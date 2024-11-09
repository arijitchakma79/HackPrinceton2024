from rag.lecture_rag import RAG  

class QueryHandler:
    def __init__(self):
        
        self.rag = RAG()

    def handle_query(self, question: str):
        """
        Handles a query by passing it to the RAG instance.
        
        Args:
            question (str): The question to be queried.
        
        Returns:
            dict: A dictionary containing the answer, sources, and titles.
        """
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

    def add_lecture_to_db(self, title: str, content: str):
        """
        Adds a lecture to the vector database by chunking the content and generating embeddings.
        
        Args:
            title (str): The title of the lecture.
            content (str): The content of the lecture.
        
        Returns:
            dict: A dictionary indicating success or failure and additional information.
        """
        try:
            if not title or not content:
                return {"error": "Both 'title' and 'content' fields are required"}

            success = self.rag.add_lecture_to_vector_db(title, content)

            if success:
                return {"message": f"Lecture '{title}' added successfully"}
            else:
                return {"error": "Failed to add lecture to the database"}
        
        except Exception as e:
            return {"error": f"An error occurred while adding the lecture: {str(e)}"}
