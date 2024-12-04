import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Define fuzzy logic variables
time_available = ctrl.Antecedent(np.array([5, 10, 20, 30, 60]), 'time_available')
proficiency_level = ctrl.Antecedent(np.arange(1, 6, 1), 'proficiency_level')
learning_task = ctrl.Consequent(np.arange(1, 6, 1), 'learning_task')

# Define membership functions for time available
time_available['minimal'] = fuzz.trimf(time_available.universe, [5, 5, 10])
time_available['short'] = fuzz.trimf(time_available.universe, [5, 10, 20])
time_available['moderate'] = fuzz.trimf(time_available.universe, [10, 20, 30])
time_available['consistent'] = fuzz.trimf(time_available.universe, [20, 30, 60])
time_available['intensive'] = fuzz.trimf(time_available.universe, [30, 60, 60])

# Define membership functions for proficiency level
proficiency_level['starter'] = fuzz.trimf(proficiency_level.universe, [1, 1, 2])
proficiency_level['beginner'] = fuzz.trimf(proficiency_level.universe, [1, 2, 3])
proficiency_level['intermediate'] = fuzz.trimf(proficiency_level.universe, [2, 3, 4])
proficiency_level['proficient'] = fuzz.trimf(proficiency_level.universe, [3, 4, 5])
proficiency_level['advanced'] = fuzz.trimf(proficiency_level.universe, [4, 5, 5])

# Define membership functions for learning task
learning_task['simple'] = fuzz.trimf(learning_task.universe, [1, 1, 2])
learning_task['easy'] = fuzz.trimf(learning_task.universe, [1, 2, 3])
learning_task['standard'] = fuzz.trimf(learning_task.universe, [2, 3, 4])
learning_task['hard'] = fuzz.trimf(learning_task.universe, [3, 4, 5])
learning_task['complex'] = fuzz.trimf(learning_task.universe, [4, 5, 5])

# Define fuzzy rules for task recommendation
rules = [
    ctrl.Rule(time_available['minimal'] & proficiency_level['starter'], learning_task['simple']),
    ctrl.Rule(time_available['minimal'] & proficiency_level['beginner'], learning_task['easy']),
    ctrl.Rule(time_available['minimal'] & proficiency_level['intermediate'], learning_task['easy']),
    ctrl.Rule(time_available['minimal'] & proficiency_level['proficient'], learning_task['standard']),
    ctrl.Rule(time_available['minimal'] & proficiency_level['advanced'], learning_task['standard']),

    ctrl.Rule(time_available['short'] & proficiency_level['starter'], learning_task['simple']),
    ctrl.Rule(time_available['short'] & proficiency_level['beginner'], learning_task['easy']),
    ctrl.Rule(time_available['short'] & proficiency_level['intermediate'], learning_task['standard']),
    ctrl.Rule(time_available['short'] & proficiency_level['proficient'], learning_task['standard']),
    ctrl.Rule(time_available['short'] & proficiency_level['advanced'], learning_task['hard']),

    ctrl.Rule(time_available['moderate'] & proficiency_level['starter'], learning_task['easy']),
    ctrl.Rule(time_available['moderate'] & proficiency_level['beginner'], learning_task['standard']),
    ctrl.Rule(time_available['moderate'] & proficiency_level['intermediate'], learning_task['standard']),
    ctrl.Rule(time_available['moderate'] & proficiency_level['proficient'], learning_task['hard']),
    ctrl.Rule(time_available['moderate'] & proficiency_level['advanced'], learning_task['hard']),

    ctrl.Rule(time_available['consistent'] & proficiency_level['starter'], learning_task['standard']),
    ctrl.Rule(time_available['consistent'] & proficiency_level['beginner'], learning_task['standard']),
    ctrl.Rule(time_available['consistent'] & proficiency_level['intermediate'], learning_task['hard']),
    ctrl.Rule(time_available['consistent'] & proficiency_level['proficient'], learning_task['hard']),
    ctrl.Rule(time_available['consistent'] & proficiency_level['advanced'], learning_task['complex']),

    ctrl.Rule(time_available['intensive'] & proficiency_level['starter'], learning_task['standard']),
    ctrl.Rule(time_available['intensive'] & proficiency_level['beginner'], learning_task['hard']),
    ctrl.Rule(time_available['intensive'] & proficiency_level['intermediate'], learning_task['hard']),
    ctrl.Rule(time_available['intensive'] & proficiency_level['proficient'], learning_task['complex']),
    ctrl.Rule(time_available['intensive'] & proficiency_level['advanced'], learning_task['complex']),
]

# Control system
learning_ctrl = ctrl.ControlSystem(rules)
learning_sim = ctrl.ControlSystemSimulation(learning_ctrl)

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

# Task index tracker for task rotation
task_index_tracker = {key: 0 for key in task_mapping.keys()}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_task', methods=['POST'])
def get_task():
    time_available_value = int(request.form['timeAvailable'])
    proficiency_level_value = int(request.form['proficiencyLevel'])

    if time_available_value not in [5, 10, 20, 30, 60] or proficiency_level_value not in [1, 2, 3, 4, 5]:
        return jsonify({'error': 'Invalid input values'}), 400

    learning_sim.input['time_available'] = time_available_value
    learning_sim.input['proficiency_level'] = proficiency_level_value

    # Perform the simulation
    learning_sim.compute()
    task_value = learning_sim.output['learning_task']

    # Calculate membership degrees for each task level
    membership_degrees = {
        level: fuzz.interp_membership(learning_task.universe, learning_task[level].mf, task_value)
        for level in task_mapping.keys()
    }

    # Ensure normalization to handle edge cases
    total_degree = sum(membership_degrees.values())
    if total_degree == 0:
        return jsonify({'error': 'Unable to determine a task.'}), 500

    probabilities = {level: degree / total_degree for level, degree in membership_degrees.items()}

    # Select a task level probabilistically
    selected_level = np.random.choice(
        list(probabilities.keys()),
        p=list(probabilities.values())
    )

    # Retrieve the task from the selected level and rotate
    task_index = task_index_tracker[selected_level]
    tasks = task_mapping[selected_level]
    recommended_task = tasks[task_index]

    # Update the rotation index
    task_index_tracker[selected_level] = (task_index + 1) % len(tasks)

    return jsonify({
        'taskLevel': selected_level,
        'taskDescription': recommended_task
    })

if __name__ == '__main__':
    app.run()