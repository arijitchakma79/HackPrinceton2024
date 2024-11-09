import uuid
from datetime import datetime
from collections import defaultdict
from typing import List, Dict
from openai import OpenAI
from database.qdrant_db import QdrantDB
from config.config import Config
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, Range

class RAG:
    def __init__(self):
        self.db = QdrantDB(Config.COLLECTION_NAME)
        self.openai = OpenAI(api_key=Config.OPENA_API_KEY)
        self.recent_chunks = []
        self.max_recent_chunks = 10
        self.session_memory = defaultdict(list)

    def _get_embedding(self, text: str) -> List[float]:
        response = self.openai.embeddings.create(
            model=Config.EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding

    def add_chunk_to_recent(self, chunk: str, course_title: str, lecture_title: str):
        self.recent_chunks.append({
            "text": chunk,
            "course_title": course_title,
            "lecture_title": lecture_title,
            "timestamp": datetime.now().isoformat()
        })
        if len(self.recent_chunks) > self.max_recent_chunks:
            self.recent_chunks.pop(0)

    def _search_recent_chunks(self, course_title: str, lecture_title: str, current_date: datetime.date, limit: int = 3) -> List[Dict]:
        results = [
            chunk for chunk in self.recent_chunks
            if chunk['course_title'] == course_title and chunk['lecture_title'] == lecture_title and
            datetime.fromisoformat(chunk['timestamp']).date() == current_date
        ]
        return results[:limit]

    def add_lecture_to_db(self, course_title: str, lecture_title: str, content: str) -> dict:
        try:
            chunks = self._chunk_text(content)
            points = []
            for position, chunk in chunks:
                embedding = self._get_embedding(chunk)
                point_id = str(uuid.uuid4())
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
                self.add_chunk_to_recent(chunk, course_title, lecture_title)
            self.db.add_points(points)
            return {"status": "success", "message": "Lecture added successfully."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to add lecture content: {str(e)}"}

    def query(self, question: str, course_title: str, lecture_title: str, prefer_recent: bool = True, limit: int = 3) -> dict:
        current_date = datetime.now().date()
        session_key = f"{course_title}_{lecture_title}_{current_date}"
        recent_results = self._search_recent_chunks(course_title, lecture_title, current_date, limit) if prefer_recent else []

        if len(recent_results) < limit:
            query_embedding = self._get_embedding(question)
            db_results = self.db.search(
                vector=query_embedding,
                filter=Filter(
                    must=[
                        FieldCondition(key="course_title", match=MatchValue(value=course_title)),
                        FieldCondition(key="lecture_title", match=MatchValue(value=lecture_title)),
                        Range(key="timestamp", gte=str(current_date))
                    ]
                ),
                limit=limit - len(recent_results)
            )
            db_parsed = [
                {
                    "text": hit.payload['text'],
                    "course_title": hit.payload['course_title'],
                    "lecture_title": hit.payload['lecture_title'],
                    "timestamp": hit.payload['timestamp']
                } for hit in db_results
            ]
            combined_results = recent_results + db_parsed
        else:
            combined_results = recent_results

        if not combined_results:
            response = self._generate_gpt_response(question)
            return {
                "answer": response,
                "sources": [],
                "titles": [],
                "from_gpt": True
            }

        combined_results.sort(key=lambda x: datetime.fromisoformat(x['timestamp']))
        contexts = [r['text'] for r in combined_results]
        response = self._generate_gpt_response_with_contexts(question, contexts)

        if response not in self.session_memory[session_key]:
            self.session_memory[session_key].append(response)

        return {
            "answer": response,
            "sources": contexts,
            "titles": [r['lecture_title'] for r in combined_results],
            "from_gpt": False
        }

    def _generate_gpt_response(self, question: str) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful teaching assistant."},
            {"role": "user", "content": question}
        ]
        response = self.openai.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

    def _generate_gpt_response_with_contexts(self, question: str, contexts: List[str]) -> str:
        messages = [
            {"role": "system", "content": "You are a helpful teaching assistant. Use the provided lecture content to answer the question."},
            {"role": "user", "content": f"Contexts: {' '.join(contexts)}\n\nQuestion: {question}"}
        ]
        response = self.openai.chat.completions.create(
            model=Config.LLM_MODEL,
            messages=messages,
            temperature=0.5
        )
        return response.choices[0].message.content

    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[tuple]:
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
