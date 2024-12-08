from flask import Flask, render_template, request, jsonify
from main.definitions import (
    get_fuzzy_controller, 
    time_available, 
    proficiency_level, 
    learning_task, 
    get_task, 
    task_mapping
)
import matplotlib.pyplot as plt
import matplotlib
import os

app = Flask(__name__)

matplotlib.use('Agg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_task', methods=['POST'])
def get_task_route():
    time_available_value = int(request.form['timeAvailable'])
    proficiency_level_value = int(request.form['proficiencyLevel'])

    # Ensure inputs are valid
    if not (0 <= time_available_value <= 50) or not (0 <= proficiency_level_value <= 5):
        return jsonify({'error': 'Invalid input values'}), 400

    # Initialize fuzzy controller
    learning_sim = get_fuzzy_controller()
    learning_sim.input['time_available'] = time_available_value
    learning_sim.input['proficiency_level'] = proficiency_level_value
    learning_sim.compute()

    # Map fuzzy output to a task level
    task_value = learning_sim.output['learning_task']
    level_index = round(task_value)
    level_name = list(task_mapping.keys())[level_index - 1]
    task = get_task(level_name)

    return jsonify({
        'taskLevel': level_name,
        'taskDescription': task
    })

@app.route('/visualizations')
def visualizations():
    # Directory to save static plots
    static_dir = os.path.join(os.getcwd(), 'static')
    os.makedirs(static_dir, exist_ok=True)

    # Generate and save the plots
    # Plot time_available
    plt.figure()
    for label in time_available.terms:
        plt.plot(time_available.universe, time_available[label].mf, label=label)
    plt.title("Time Available Membership Functions")
    plt.legend()
    plt.savefig(os.path.join(static_dir, 'time_available.png'))
    plt.close()

    # Plot proficiency_level
    plt.figure()
    for label in proficiency_level.terms:
        plt.plot(proficiency_level.universe, proficiency_level[label].mf, label=label)
    plt.title("Proficiency Level Membership Functions")
    plt.legend()
    plt.savefig(os.path.join(static_dir, 'proficiency_level.png'))
    plt.close()

    # Plot learning_task
    plt.figure()
    for label in learning_task.terms:
        plt.plot(learning_task.universe, learning_task[label].mf, label=label)
    plt.title("Learning Task Membership Functions")
    plt.legend()
    plt.savefig(os.path.join(static_dir, 'learning_task.png'))
    plt.close()

    # Render the template with static paths
    return render_template('visualizations.html')

if __name__ == '__main__':
    app.run()