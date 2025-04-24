from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import logging

# --- Basic Configuration ---
app = Flask(__name__)
# IMPORTANT: Configure CORS appropriately for your deployment.
# For development, allowing all origins is often easiest.
# For production, restrict it to your frontend's domain.
# Example: CORS(app, resources={r"/api/*": {"origins": "https://your-frontend-domain.com"}})
CORS(app) # Allow all origins by default for simplicity here

logging.basicConfig(level=logging.INFO)

# --- In-Memory Data Store ---
# WARNING: This data is NOT persistent. It will be lost if the server restarts.
# For persistence, consider using a file (JSON, CSV), SQLite, or a proper database.
drink_data = {
    # "Example User": 2 # Example structure
}

# --- Helper Functions ---
def calculate_total():
    """Calculates the sum of all drink counts."""
    return sum(drink_data.values())

# --- API Endpoints ---

@app.route('/api/data', methods=['GET'])
def get_data():
    """Returns the current state: all users, counts, and total."""
    logging.info("GET /api/data requested")
    return jsonify({
        "users": drink_data,
        "total_drinks": calculate_total()
    })

@app.route('/api/user', methods=['POST'])
def add_user():
    """Adds a new user with a count of 0."""
    if not request.json or 'name' not in request.json:
        logging.warning("POST /api/user - Bad request: Missing 'name'")
        abort(400, description="Missing 'name' in request body")

    name = request.json['name'].strip()
    if not name:
        logging.warning("POST /api/user - Bad request: Empty 'name'")
        abort(400, description="User name cannot be empty")

    if name in drink_data:
        logging.warning(f"POST /api/user - Conflict: User '{name}' already exists")
        abort(409, description=f"User '{name}' already exists") # 409 Conflict

    drink_data[name] = 0
    logging.info(f"User '{name}' added.")
    return jsonify({"message": f"User '{name}' added successfully", "users": drink_data, "total_drinks": calculate_total()}), 201 # 201 Created

@app.route('/api/user/<username>', methods=['DELETE'])
def delete_user(username):
    """Deletes a user and their count."""
    if username not in drink_data:
        logging.warning(f"DELETE /api/user/{username} - Not found")
        abort(404, description=f"User '{username}' not found")

    del drink_data[username]
    logging.info(f"User '{username}' deleted.")
    return jsonify({"message": f"User '{username}' deleted successfully", "users": drink_data, "total_drinks": calculate_total()})

@app.route('/api/drink/<username>', methods=['POST'])
def add_drink(username):
    """Increments the drink count for a user."""
    if username not in drink_data:
        logging.warning(f"POST /api/drink/{username} - Not found")
        abort(404, description=f"User '{username}' not found")

    drink_data[username] += 1
    logging.info(f"Drink added for '{username}'. New count: {drink_data[username]}")
    return jsonify({"message": "Drink added", "name": username, "count": drink_data[username], "total_drinks": calculate_total()})

@app.route('/api/drink/<username>', methods=['DELETE'])
def remove_drink(username):
    """Decrements the drink count for a user, minimum 0."""
    if username not in drink_data:
        logging.warning(f"DELETE /api/drink/{username} - Not found")
        abort(404, description=f"User '{username}' not found")

    if drink_data[username] > 0:
        drink_data[username] -= 1
        logging.info(f"Drink removed for '{username}'. New count: {drink_data[username]}")
        return jsonify({"message": "Drink removed", "name": username, "count": drink_data[username], "total_drinks": calculate_total()})
    else:
        logging.info(f"Drink count for '{username}' already 0. No change.")
        # Return success even if count is 0, as the state is still valid
        return jsonify({"message": "Drink count already 0", "name": username, "count": 0, "total_drinks": calculate_total()})


@app.route('/api/reset', methods=['POST'])
def reset_counts():
    """Resets all user counts to 0."""
    for user in drink_data:
        drink_data[user] = 0
    logging.info("All drink counts reset to 0.")
    return jsonify({"message": "All counts reset successfully", "users": drink_data, "total_drinks": 0})

# --- Error Handlers ---
@app.errorhandler(400)
def bad_request(error):
    return jsonify(error=str(error.description)), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify(error=str(error.description)), 404

@app.errorhandler(409)
def conflict(error):
    return jsonify(error=str(error.description)), 409

# --- Run the App ---
if __name__ == '__main__':
    # Host '0.0.0.0' makes it accessible on your network
    # Debug=True is helpful for development (auto-reloads), but
    # **NEVER** use debug=True in a production environment!
    app.run(host='0.0.0.0', port=5000, debug=False) # Set debug=False for production/VPS
