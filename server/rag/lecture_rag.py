import uuid
from openai import OpenAI
from database.qdrant_db import QdrantDB
from datetime import datetime
from typing import List, Dict
from config.config import Config
from qdrant_client.models import PointStruct

class RAG:
    def __init__(self):
        self.db = QdrantDB(Config.CollectionName)
        self.openai = OpenAI(api_key=Config.OPENA_API_KEY)

    def _get_embedding(self, text: str) -> List[float]:
        response = self.openai.embeddings.create(
            model=Config.EmbeddingModel,
            input=text
        )
        return response.data[0].embedding

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        words = text.split()
        chunks = []
        current_chunks = []
        current_size = 0

        for word in words:
            current_chunks.append(word)
            current_size += len(word) + 1  

            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunks))
                current_chunks = []
                current_size = 0

        if current_chunks:
            chunks.append(" ".join(current_chunks))

        return chunks

    def add_lecture_to_vector_db(self, course_title: str, lecture_title: str, content: str) -> bool:
        """Add lecture content to the vector database."""
        try:
            chunks = self._chunk_text(content)
            points = []

            for i, chunk in enumerate(chunks):
                embedding = self._get_embedding(chunk)
                point_id = str(uuid.uuid4())
                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "course_title": course_title,
                        "lecture_title": lecture_title,
                        "text": chunk,
                        "chunk_id": i,
                        "timestamp": datetime.now().isoformat()
                    }
                ))

            self.db.add_points(points)
            print(f"Added lecture '{lecture_title}' from course '{course_title}' with {len(chunks)} segments")
            return True

        except Exception as e:
            print(f"Error adding lecture: {str(e)}")
            return False

    def query(self, question: str, limit: int = 3) -> Dict:
        try:
            query_embedding = self._get_embedding(question)

            results = self.db.search(query_embedding, limit)
            
            # Extract relevant data from the search results
            contexts = [hit.payload['text'] for hit in results]
            courses = [hit.payload['course_title'] for hit in results]
            lectures = [hit.payload['lecture_title'] for hit in results]  
            
            course_info = "\n".join(
                f"From course: '{course}', lecture: '{lecture}'"
                for course, lecture in zip(courses, lectures)
            )

            messages = [
                {"role": "system", "content": "You are a helpful assistant knowledgeable in various courses and lectures. Use the provided lecture segments to answer questions and provide context where necessary."},
                {"role": "user", "content": f"""
                Lecture segments:
                {' '.join(contexts)}

                Context:
                {course_info}

                Question: {question}
                """}
            ]

            response = self.openai.chat.completions.create(
                model=Config.LLM_model,
                messages=messages,
                temperature=0
            )

            return {
                "answer": response.choices[0].message.content,
                "sources": contexts,
                "titles": lectures,  
                "course_info": course_info
            }

        except Exception as e:
            print(f"Error querying: {str(e)}")
            return {"error": f"An error occurred while processing the query: {str(e)}"}
