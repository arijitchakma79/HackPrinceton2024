from rag.rag import RAG

rag_instance = RAG()

def add_lecture_handler(course_title: str, lecture_title: str, content: str) -> dict:
    result = rag_instance.add_lecture_to_db(course_title, lecture_title, content)
    return result

def query_handler_function(question: str, course_title: str, lecture_title: str, prefer_recent: bool = True, limit: int = 3) -> dict:
    response = rag_instance.query(question, course_title, lecture_title, prefer_recent, limit)
    return response
