import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Define fuzzy variables
time_available = ctrl.Antecedent(np.arange(0, 51, 1), 'time_available')
proficiency_level = ctrl.Antecedent(np.arange(0, 6, 1), 'proficiency_level')
learning_task = ctrl.Consequent(np.arange(0, 6, 1), 'learning_task')

# Define membership functions
time_available['minimal'] = fuzz.trimf(time_available.universe, [0, 10, 20])
time_available['short'] = fuzz.trimf(time_available.universe, [10, 20, 30])
time_available['moderate'] = fuzz.trimf(time_available.universe, [20, 30, 40])
time_available['consistent'] = fuzz.trimf(time_available.universe, [30, 40, 50])
time_available['intensive'] = fuzz.trimf(time_available.universe, [40, 50, 51])

proficiency_level['starter'] = fuzz.trimf(proficiency_level.universe, [0, 1, 2])
proficiency_level['beginner'] = fuzz.trimf(proficiency_level.universe, [1, 2, 3])
proficiency_level['intermediate'] = fuzz.trimf(proficiency_level.universe, [2, 3, 4])
proficiency_level['proficient'] = fuzz.trimf(proficiency_level.universe, [3, 4, 5])
proficiency_level['advanced'] = fuzz.trimf(proficiency_level.universe, [4, 5, 6])

learning_task['simple'] = fuzz.trimf(learning_task.universe, [0, 1, 2])
learning_task['easy'] = fuzz.trimf(learning_task.universe, [1, 2, 3])
learning_task['standard'] = fuzz.trimf(learning_task.universe, [2, 3, 4])
learning_task['hard'] = fuzz.trimf(learning_task.universe, [3, 4, 5])
learning_task['complex'] = fuzz.trimf(learning_task.universe, [4, 5, 6])

# Define rules
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

# Create the fuzzy controller
def get_fuzzy_controller():
    learning_ctrl = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(learning_ctrl)