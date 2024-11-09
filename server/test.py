import requests
import time

# Define the API endpoint for adding lecture content
ADD_LECTURE_URL = 'http://localhost:5000/add_lecture'

# Extended lecture content to be sent in chunks
lecture_chunks = [
    "Good morning, class. Today, we are diving into the fundamentals of machine learning, a crucial aspect of artificial intelligence.",
    "Machine learning enables computers to learn from data and make decisions or predictions without being explicitly programmed.",
    "There are three main types of machine learning: supervised, unsupervised, and reinforcement learning.",
    "In supervised learning, we use labeled datasets to train algorithms that can classify data or predict outcomes.",
    "For example, a model trained with images labeled as 'cat' or 'dog' learns to classify future images.",
    "Unsupervised learning, however, does not use labeled data. It finds hidden patterns and structures in data, such as clustering similar items together.",
    "Think about algorithms used for market segmentation or recommendations, where no prior labels are provided.",
    "Reinforcement learning is quite different from the previous types. It focuses on training agents to make sequences of decisions through a system of rewards and penalties.",
    "For instance, teaching a robot to navigate a maze by rewarding correct moves and penalizing dead ends.",
    "Now, before we move forward, I want to remind you that Homework 10 is due next week. It covers concepts from both supervised and unsupervised learning, so please review your notes.",
    "Homework 10 will test your understanding of decision trees, support vector machines, and clustering algorithms.",
    "Remember, you can ask questions during office hours or in the discussion forum if you run into any difficulties with the assignment.",
    "Continuing on, in reinforcement learning, popular algorithms include Q-learning and Deep Q Networks (DQN). These are used in training complex systems, like self-driving cars or game-playing agents.",
    "Another important point is the final exam. It will cover all the material we have discussed so far, including supervised, unsupervised, and reinforcement learning.",
    "The exam is comprehensive and will take place in two weeks. Make sure to go over lecture notes, assignments, and previous quizzes.",
    "Today's lecture also introduces evaluation metrics for machine learning models. These include accuracy, precision, recall, and F1-score.",
    "Understanding these metrics is essential when assessing the performance of classification models.",
    "For homework 10, you will need to implement and evaluate a model using these metrics, so I highly recommend practicing with sample data sets.",
    "Finally, we will touch on the importance of cross-validation. This technique helps to ensure that your model generalizes well to new, unseen data.",
    "Cross-validation splits the data into parts to train and test the model multiple times, giving a better estimate of its performance.",
    "Alright, that concludes today's main points. Please remember to start early on Homework 10, and don't hesitate to prepare questions for the next class or office hours.",
    "And, as always, make sure to keep track of deadlines. The final exam is coming up, so plan your study time accordingly."
]

# Define the metadata for the lecture
course_title = "Introduction to AI"
lecture_title = "Machine Learning Basics and Evaluation Metrics"

# Simulate sending chunks to the backend as if they were being delivered in real-time
for chunk in lecture_chunks:
    payload = {
        "course_title": course_title,
        "lecture_title": lecture_title,
        "content": chunk
    }
    
    # Send the chunk to the backend
    response = requests.post(ADD_LECTURE_URL, json=payload)
    
    # Print the response for confirmation
    if response.status_code == 200:
        print(f"Chunk sent successfully: {chunk[:60]}...")  # Print the start of the chunk for brevity
    else:
        print(f"Failed to send chunk: {chunk[:60]} - Status Code: {response.status_code}")
    
    # Wait a few seconds to simulate real-time delivery
    time.sleep(5)  # Adjust the sleep time as needed to simulate a delay between content delivery
