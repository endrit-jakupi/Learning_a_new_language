from flask import Flask, render_template, request, jsonify
from main.fuzzy_system import (
    get_fuzzy_controller, 
    time_available, 
    proficiency_level, 
    learning_task, 
    get_task, 
    task_mapping
)
from database.models import Feedback
from database.connection import db, migrate
import matplotlib.pyplot as plt
import matplotlib
import os

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user_feedback_df6m_user:NwP2UuliOhxXSfqcO7fcaXDzBlDED43q@dpg-ctapq18gph6c73er5ij0-a.oregon-postgres.render.com/user_feedback_df6m'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate.init_app(app, db)

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

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    task_description = request.form['task_description']
    feedback_rating = request.form['feedback_rating']

    if not task_description or not feedback_rating:
        return jsonify({'error': 'Task and feedback rating are required.'}), 400

    try:
        new_feedback = Feedback(
            task_description=task_description,
            feedback_rating=feedback_rating
        )
        db.session.add(new_feedback)
        db.session.commit()

        return jsonify({'status': 'success', 'message': 'Thank you for your feedback!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualizations')
def visualizations():
    # Directory to save static plots
    static_dir = os.path.join(os.getcwd(), 'static')
    os.makedirs(static_dir, exist_ok=True)

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

    return render_template('visualizations.html')

if __name__ == '__main__':
    app.run()