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

# Return the main page
@app.route('/')
def index():
    return render_template('index.html')

# Process input and return recommended task
@app.route('/get_task', methods=['POST'])
def get_task():
    time_available_value = int(request.form['timeAvailable'])
    proficiency_level_value = int(request.form['proficiencyLevel'])

    if time_available_value not in [5, 10, 20, 30, 60] or proficiency_level_value not in [1, 2, 3, 4, 5]:
        return jsonify({'error': 'Invalid input values'}), 400

    learning_sim.input['time_available'] = time_available_value
    learning_sim.input['proficiency_level'] = proficiency_level_value

    learning_sim.compute()

    task_value = learning_sim.output['learning_task']

    task_mapping = {
        1: "Talk about recent experiences, any special event that you attended, or something interesting you learned recently.",
        2: "Read a short piece of text and summarize or discuss the main ideas in your own words.",
        3: "Write a summary of something you came across recently, like a story, video, or event, and mention the main point of it.",
        4: "Practice speaking with a native speaker or a friend and discuss a topic that challenges your language skills.",
        5: "Prepare a persuasive speech on a challenging topic and present or discuss reasons to support your perspective."
    }

    task_id = int(np.round(task_value))
    return jsonify({'task': task_id, 'taskDescription': task_mapping[task_id]})

if __name__ == '__main__':
    app.run()