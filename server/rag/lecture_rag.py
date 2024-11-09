import uuid
from openai import OpenAI
from database.qdrant_db import QdrantDB
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config.config import Config
from qdrant_client.models import PointStruct, Filter, FieldCondition, Range

class RAG:
    def __init__(self):
        self.db = QdrantDB(Config.CollectionName)
        self.openai = OpenAI(api_key=Config.OPENA_API_KEY)
        self.recent_chunks = []  # Store recent chunks in memory
        self.max_recent_chunks = 10  # Adjust based on your needs

    def _get_embedding(self, text: str) -> List[float]:
        response = self.openai.embeddings.create(
            model=Config.EmbeddingModel,
            input=text
        )
        return response.data[0].embedding

    def add_chunk_to_recent(self, chunk: str, course_title: str, lecture_title: str, position: int):
        """Add a new chunk to recent memory with timestamp."""
        self.recent_chunks.append({
            "text": chunk,
            "course_title": course_title,
            "lecture_title": lecture_title,
            "position": position,
            "timestamp": datetime.now()
        })
        # Keep only recent chunks
        if len(self.recent_chunks) > self.max_recent_chunks:
            self.recent_chunks.pop(0)

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[tuple]:
        """Return chunks with position information"""
        words = text.split()
        chunks = []
        current_chunks = []
        current_size = 0
        position = 0

        for word in words:
            current_chunks.append(word)
            current_size += len(word) + 1

            if current_size >= chunk_size:
                chunks.append((position, " ".join(current_chunks)))
                current_chunks = []
                current_size = 0
                position += 1

        if current_chunks:
            chunks.append((position, " ".join(current_chunks)))

        return chunks

    def add_lecture_to_vector_db(self, course_title: str, lecture_title: str, content: str) -> bool:
        """Add lecture content to the vector database and recent memory."""
        try:
            chunks = self._chunk_text(content)
            points = []

            for position, chunk in chunks:
                embedding = self._get_embedding(chunk)
                point_id = str(uuid.uuid4())
                
                # Add to vector database
                points.append(PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "course_title": course_title,
                        "lecture_title": lecture_title,
                        "text": chunk,
                        "position": position,
                        "timestamp": datetime.now().isoformat()
                    }
                ))
                
                # Add to recent memory
                self.add_chunk_to_recent(chunk, course_title, lecture_title, position)

            self.db.add_points(points)
            return True

        except Exception as e:
            print(f"Error adding lecture: {str(e)}")
            return False

    def _search_recent_chunks(self, question: str, limit: int = 3) -> List[Dict]:
        """Search through recent chunks using embeddings."""
        if not self.recent_chunks:
            return []

        query_embedding = self._get_embedding(question)
        chunk_scores = []

        for chunk in self.recent_chunks:
            chunk_embedding = self._get_embedding(chunk["text"])
            # Calculate cosine similarity
            similarity = sum(a * b for a, b in zip(query_embedding, chunk_embedding))
            chunk_scores.append((similarity, chunk))

        # Sort by similarity and return top matches
        chunk_scores.sort(reverse=True, key=lambda x: x[0])
        return [chunk for _, chunk in chunk_scores[:limit]]

    def query(self, question: str, prefer_recent: bool = True, limit: int = 3) -> Dict:
        """
        Query the system with preference for recent content.
        prefer_recent: If True, prioritize recent chunks and only fall back to database if needed
        """
        try:
            # First check recent chunks
            recent_results = self._search_recent_chunks(question, limit) if prefer_recent else []
            
            # If we don't have enough recent results, search the database
            if len(recent_results) < limit:
                query_embedding = self._get_embedding(question)
                db_results = self.db.search(query_embedding, limit=limit - len(recent_results))
                db_parsed = [
                    {
                        "text": hit.payload['text'],
                        "course_title": hit.payload['course_title'],
                        "lecture_title": hit.payload['lecture_title'],
                        "position": hit.payload.get('position', 0),
                        "timestamp": hit.payload['timestamp']
                    } for hit in db_results
                ]
                combined_results = recent_results + db_parsed
            else:
                combined_results = recent_results

            if not combined_results:
                # If no results found, use GPT for general knowledge
                messages = [
                    {"role": "system", "content": "You are a helpful teaching assistant. The following question was not covered in the lecture, so provide a general answer and mention this fact."},
                    {"role": "user", "content": question}
                ]
                
                response = self.openai.chat.completions.create(
                    model=Config.LLM_model,
                    messages=messages,
                    temperature=0.7
                )
                
                return {
                    "answer": response.choices[0].message.content,
                    "sources": [],
                    "titles": [],
                    "from_gpt": True
                }

            # Sort results by timestamp to maintain chronological order
            # Use get() for position to handle cases where it might be missing
            combined_results.sort(key=lambda x: x.get('position', 0))
            
            contexts = [r['text'] for r in combined_results]
            courses = [r['course_title'] for r in combined_results]
            lectures = [r['lecture_title'] for r in combined_results]
            
            course_info = "\n".join(
                f"From course: '{course}', lecture: '{lecture}'"
                for course, lecture in zip(courses, lectures)
            )

            messages = [
                {"role": "system", "content": """You are a helpful teaching assistant. 
                Use the provided lecture segments to answer questions. If the information comes from recent segments,
                mention that this was just discussed. If you're using older segments, indicate that this was covered earlier."""},
                {"role": "user", "content": f"""
                Lecture segments (in chronological order):
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
                "course_info": course_info,
                "from_recent": any(r in recent_results for r in combined_results),
                "from_gpt": False
            }

        except Exception as e:
            print(f"Error querying: {str(e)}")
            return {"error": f"An error occurred while processing the query: {str(e)}"}