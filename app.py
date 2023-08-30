from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import string, random

def generate_random_string(length=8):
    # Generates a random string of a given length
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite for simplicity; you can use others
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# DATA MODELS

class Participant(db.Model):
    id = db.Column(db.String, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)  # Added this field
    country_of_birth = db.Column(db.String, nullable=False)  # Added this field
    nivel_estudios = db.Column(db.String, nullable=False)
    # ... other demographic data ...


class SemanticTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.String, db.ForeignKey('participant.id'), nullable=False)
    cue_word = db.Column(db.String, nullable=False)
    selected_words = db.Column(db.String, nullable=False)  # Storing words as comma-separated string



# This secret key should ideally be in a config file and not hardcoded.
app.secret_key = 'supersecretkey'

cue_and_targets = [
    {"cue": "apple", "targets": ["fruit", "banana", "car", "train", ...]},
    {"cue": "dog", "targets": ["animal", "cat", "bus", "plane", ...]},
    # ... add more ...
]


@app.route('/sociodemo', methods=['GET', 'POST'])
def sociodemo():
    if request.method == 'POST':
        # Suppose you generate or assign participant_id here
        gender = request.form.get('gender')
        country_of_birth = request.form.get('country_of_birth')
        nivel_estudios = request.form.get('nivel_estudios')

        # Generate or assign participant_id
        participant_id = generate_random_string()

        # Store the participant ID in session for later use
        session["participant_id"] = participant_id

        # Create a new participant object and add to the database
        new_participant = Participant(id=participant_id, gender=gender, country_of_birth=country_of_birth,nivel_estudios=nivel_estudios)
        db.session.add(new_participant)
        db.session.commit()

        # Rest of the code (like saving sociodemographic info)...
        # ...

        # Redirect to semantic_similarity_drag
        return redirect(url_for('semantic_similarity_drag'))
    return render_template('sociodemo/sociodemo.html')





# Semantic Similarity Route
@app.route('/semantic_similarity_drag', methods=['GET', 'POST'])
def semantic_similarity_drag():
    # Initialize the current index in session if it doesn't exist
    session.setdefault("current_index", 0)

    # Check if current index is out of range
    if session["current_index"] >= len(cue_and_targets):
        return "All tasks completed. Thank you!"  # You can customize this response or redirect as needed

    data = cue_and_targets[session["current_index"]]
    return render_template('semantic_similarity/drag.html', cue_word=data["cue"], target_words=data["targets"])


@app.route('/similarity_save_response', methods=['POST'])
def save_response():
    selected_words = request.form.getlist('words[]')

    # Retrieve the participant_id from the session
    participant_id = session.get("participant_id")
    if not participant_id:
        return jsonify(status="error", message="No participant ID found")

    cue_word = cue_and_targets[session["current_index"]]['cue']
    entry = SemanticTask(participant_id=participant_id, cue_word=cue_word, selected_words=",".join(selected_words))
    db.session.add(entry)
    db.session.commit()

    # Move to the next cue and target set
    session["current_index"] += 1

    if session["current_index"] < len(cue_and_targets):
        return jsonify(status="success", message="Data saved successfully.")
    else:
        return jsonify(status="completed", message="All tasks completed.")




# reset sem index
@app.route('/reset_index')
def reset_index():
    session["current_index"] = 0
    return "Index reset to 0"

# Feature Rating Route
@app.route('/feature_rating', methods=['GET', 'POST'])
def feature_rating_route():
    # You'd put the logic for the feature rating task here. 
    # For now, I'll just return a placeholder template.
    return render_template('feature_rating/rate.html')

if __name__ == "__main__":
    app.run(debug=True)
