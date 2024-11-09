from rag.lecture_rag import RAG

def main():
    # Initialize RAG system
    rag = RAG()
    
    # Example lecture
    lecture = """
    Hi! I'm Christina. I'm currently studying at Rhode Island School of Design for industrial design. I deeply care about using industrial design to innovate biomedical products that practice Human-Centered Design Thinking; and use illustrations combined with digital technology to revolutionize scientific communications to be representative, effective, and accessible.
    """
    
    # Add lecture
    rag.add_lecture_to_vector_db("Neural Networks Intro", lecture)
    
    # Test query
    question = "Make major keypoints about Christina"
    result = rag.query(question)
    
    if result:
        print("\nQuestion:", question)
        print("\nAnswer:", result["answer"])
        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source}")

if __name__ == "__main__":
    main()