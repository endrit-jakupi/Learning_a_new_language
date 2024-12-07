# Task mapping
task_mapping = {
    'simple': [
        "Practice introducing yourself and sharing a few facts about yourself.",
        "Describe a typical day in your life and what you usually do.",
        "Practice a short conversation about a simple topic."
    ],
    'easy': [
        "Talk about a recent experience or special event you attended.",
        "Pretend you need to ask for information. Practice what you would say.",
        "Give simple instructions for completing a task or solving a problem."
    ],
    'standard': [
        "Talk about your daily schedule and mention any times when it changes.",
        "Describe a personal experience and highlight the best moments of it.",
        "Pretend you’re planning a small event. Explain what it is and how you would organize it."
    ],
    'hard': [
        "Discuss your opinion on a topic that interests you and explain your reasons in detail.",
        "Talk about a significant event in your life and explain how it changed your perspective.",
        "Compare and contrast two ideas, such as living in a city versus the countryside, and explain which you prefer and why."
    ],
    'complex': [
        "Pretend you are hosting a Q&A session. Answer questions about a topic you are knowledgeable about in a clear and concise manner.",
        "Analyze a fictional or real scenario, describe the problem, and propose a detailed solution with justifications.",
        "Participate in a debate, and share your perspective about the topic."
    ]
}

# Track task rotation
task_index_tracker = {key: 0 for key in task_mapping.keys()}

def get_task(level):
    """Retrieve the next task for a given level."""
    if level not in task_mapping:
        return None

    task_index = task_index_tracker[level]
    task = task_mapping[level][task_index]
    task_index_tracker[level] = (task_index + 1) % len(task_mapping[level])

    return task