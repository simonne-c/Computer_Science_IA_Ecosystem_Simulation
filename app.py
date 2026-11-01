# Flask connects the webpage to the Python program.
from flask import Flask, render_template, request, jsonify
import json
from simulation.environment import Environment
from simulation.simulation import Simulation


app = Flask(__name__)


# Load the choices and species information from JSON.
with open("data/environments.json", "r") as file:
    environment_data = json.load(file)


# This stores the simulation that is currently running.
current_simulation = None




# Show the main webpage.
@app.route("/")
def home():
    return render_template("index.html")




# Send the available choices to JavaScript.
@app.route("/environment-options")
def environment_options():
    return jsonify(environment_data)




# Create a new simulation.
@app.route("/create-environment", methods=["POST"])
def create_environment():
    global current_simulation


    data = request.get_json()


    terrain = data["terrain"]
    climate = data["climate"]
    resources = data["resources"]
    choices = data["organisms"]


    # Make sure three different species were selected.
    selected_species = []


    for choice in choices:
        selected_species.append(choice["type"])


    if len(selected_species) != 3:
        return jsonify({"error": "Choose three organisms."}), 400


    if len(set(selected_species)) != 3:
        return jsonify({"error": "Choose three different species."}), 400


    # Make sure resource values are valid.
    for name in ["food", "water", "shelter"]:
        number = int(resources[name])


        if number < 0 or number > 100:
            return jsonify({"error": "Resources must be between 0 and 100."}), 400


        resources[name] = number


    # Create the environment object.
    environment = Environment(
        terrain,
        climate,
        environment_data["terrains"][terrain],
        environment_data["climates"][climate],
        resources
    )


    # Create the simulation.
    current_simulation = Simulation(
        environment,
        choices,
        environment_data["organisms"]
    )


    return jsonify({
        "success": True,
        "state": current_simulation.get_state()
    })




# Run one step of the simulation.
@app.route("/simulate-step", methods=["POST"])
def simulate_step():
    if current_simulation is None:
        return jsonify({"error": "Create a simulation first."}), 400


    current_simulation.step()


    return jsonify({
        "success": True,
        "state": current_simulation.get_state()
    })




# Reset the current simulation.
@app.route("/reset-simulation", methods=["POST"])
def reset_simulation():
    if current_simulation is None:
        return jsonify({"error": "Create a simulation first."}), 400


    current_simulation.reset()


    return jsonify({
        "success": True,
        "state": current_simulation.get_state()
    })




# Save the choices to a JSON file.
@app.route("/save-configuration", methods=["POST"])
def save_configuration():
    data = request.get_json()


    with open("data/saved_configuration.json", "w") as file:
        json.dump(data, file, indent=4)


    return jsonify({
        "success": True,
        "message": "Configuration saved."
    })




# Load the saved choices.
@app.route("/load-configuration")
def load_configuration():
    try:
        with open("data/saved_configuration.json", "r") as file:
            data = json.load(file)


        return jsonify({
            "success": True,
            "configuration": data
        })


    except FileNotFoundError:
        return jsonify({
            "success": False,
            "error": "No saved configuration found."
        }), 404




if __name__ == "__main__":
    app.run(debug=True)
