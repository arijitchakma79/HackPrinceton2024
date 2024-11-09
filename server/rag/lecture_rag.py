from openai import OpenAI
from database.qdrant_db import QdrantDB
from datetime import datetime
from typing import List, Dict
from config.config import Config
from qdrant_client.models import PointStruct

class RAG():
    def __init__(self):
        self.db = QdrantDB(Config.CollectionName)
        self.openai = OpenAI(api_key=Config.OPENA_API_KEY)

    def _get_embedding(self, text:str)->List[float]:
        "Get the openAI embedding for text"
        response = self.openai.embeddings.create(
            model=Config.EmbeddingModel,
            input=text
        )

        return response.data[0].embedding
    
    def _chunk_text(self, text:str, chunk_size: int = 500) -> List[str]:
        words = text.split()
        chunks = []
        current_chunks = []
        current_size = 0

        for word in words:
            current_chunks.append(word)
            current_size+= len(word)+1

            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunks))
                current_chunks = []
                current_size = 0

        if current_chunks:
            chunks.append(" ".join(current_chunks))

        return chunks
    
    def add_lecture_to_vector_db(self, title:str, content: str) -> bool:
        try:
            chunks = self._chunk_text(content)
            points = []

            for i, chunk in enumerate(chunks):
                embedding = self._get_embedding(chunk)
                points.append(PointStruct(
                    id=hash(f"{title}_{i}"),
                    vector=embedding, 
                    payload={
                        "text": chunk,
                        "title": title,
                        "chunk_id": i,
                        "timestamp": datetime.now().isoformat()
                    }
                ))

            self.db.add_points(points)
            print(f"Added lecture '{title}' with {len(chunks)} segments")
            return True
        
        except Exception as e:
            print(f"Error adding lecture: {str(e)}")
            return False
        
    def query(self, question: str, limit: int=3)->Dict:
        try:
            query_embedding = self._get_embedding(question)

            results = self.db.search(query_embedding, limit)    
            contexts = [hit.payload['text'] for hit in results]

            messages = [
                {"role": "system", "content": """You are a helpful assistant that answers questions about lecture content.
                Use only the provided lecture segments to answer questions.
                If you cannot find the answer in the segments, say so clearly."""},
                {"role": "user", "content": f"""
                Use these lecture segments to answer the question:
                
                Lecture segments:
                {' '.join(contexts)}
                
                Question: {question}
                """}
            ]


            response = self.openai.chat.completions.create(
                model = Config.LLM_model,
                messages=messages,
                temperature=0
            )

            return {
                "answer": response.choices[0].message.content,
                "sources": contexts,
                "titles": [hit.payload["title"] for hit in results]
            }
        
        except Exception as e:
            print(f"Error querying: {str(e)}")
            return None