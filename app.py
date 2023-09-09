from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import string, random, logging, stimuli
import os

#logging.basicConfig(filename='app.log', level=logging.DEBUG)


def generate_random_string(length=8):
    # Generates a random string of a given length
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# DATA MODELS

class Participant(db.Model):
    id = db.Column(db.String, primary_key=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)  # Added this field
    country_of_residence = db.Column(db.String, nullable=False)  # Added this field
    nivel_estudios = db.Column(db.String, nullable=False)
    primary_language = db.Column(db.String, nullable=False)
    # ... other demographic data ...


class SemanticTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False) #category as a string!
    participant_id = db.Column(db.String, db.ForeignKey('participant.id'), nullable=False)
    cue_word = db.Column(db.String, nullable=False)
    selected_words = db.Column(db.String, nullable=False)  # Storing words as comma-separated string

class DimensionTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False) #category as a string!
    participant_id = db.Column(db.String, db.ForeignKey('participant.id'), nullable=False)
    cue_word = db.Column(db.String, nullable=False)
    dim = db.Column(db.String, nullable=False)  #dimension coordinates as signed Integer
    rating = db.Column(db.Integer, nullable=False)  #dimension coordinates as signed Integer
    
# This secret key should ideally be in a config file and not hardcoded.
app.secret_key = 'supersecretkey'

# LOAD STIMULI

categories = stimuli.get_cats(3,BASE_DIR) # this gives 3 random categories
cat_cue_targets = stimuli.gen_cue_cats(categories)
list_of_categories = list(categories.keys())


# list of categories for feature task

categories_feat = stimuli.get_cats(3,BASE_DIR) # this gives 3 random categories, a dictionary with cat name as keys, and cue words as values
cat_dimensions = stimuli.get_dimensions(categories_feat,BASE_DIR) # dict with cate name as keys, list of dimensions (each dimension is a list of two poles) as values
list_of_categories_feat = list(categories_feat.keys())



# ITINERARY
# index -> info -> consentimiento -> intro -> sociodemo -> instrucciones_drag  -> semantic_similarity_drag  (similarity_save_response)  -> instrucciones_rating -> feature_rating (feature_save)-> gracias

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        return redirect(url_for('info'))
    return render_template('index/index.html')


@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method == 'POST':
        return redirect(url_for('consentimiento'))
    return render_template('info/info.html')


@app.route('/consentimiento', methods=['GET', 'POST'])
def consentimiento():
    return render_template('info/consentimiento.html')

@app.route('/gracias_igual', methods=['GET', 'POST'])
def gracias_igual():
    return render_template('index/gracias.html')


@app.route('/intro', methods=['GET', 'POST'])
def intro():
    return render_template('index/intro.html')


@app.route('/gracias', methods=['GET', 'POST'])
def gracias():
    return render_template('info/gracias.html')

@app.route('/instrucciones_drag', methods=['GET', 'POST'])
def instrucciones_drag():
    return render_template('semantic_similarity/intro.html')

@app.route('/instrucciones_feat', methods=['GET', 'POST'])
def instrucciones_feat():
    return render_template('feature_rating/intro.html')



@app.route('/sociodemo', methods=['GET', 'POST'])
def sociodemo():
    if request.method == 'POST':
        # Suppose you generate or assign participant_id here
        gender = request.form.get('gender')
        age = request.form.get('age')
        country_of_residence = request.form.get('country_of_birth')
        nivel_estudios = request.form.get('nivel_estudios')
        primary_language = request.form.get('language')
        
        # Generate or assign participant_id
        participant_id = generate_random_string()
        # Store the participant ID in session for later use
        session["participant_id"] = participant_id

        # Create a new participant object and add to the database
        new_participant = Participant(id=participant_id, age=age,gender=gender, country_of_residence=country_of_residence,nivel_estudios=nivel_estudios,primary_language=primary_language)
        db.session.add(new_participant)
        db.session.commit()

        # Rest of the code (like saving sociodemographic info)...
        # ...

        # Redirect to semantic_similarity_drag
        return redirect(url_for('instrucciones_drag'))
    return render_template('sociodemo/sociodemo.html')





# Semantic Similarity Route
@app.route('/semantic_similarity_drag', methods=['GET', 'POST'])
def semantic_similarity_drag():
    # Initialize the current index in session if it doesn't exist
    session.setdefault("word_index", 0)
    session.setdefault("category_index", 0)



    current_category = list_of_categories[session["category_index"]]
    cue_and_targets = cat_cue_targets[current_category]

    # Check if current index is out of range
    if session["word_index"] >= len(cue_and_targets):
        return "All tasks completed. Thank you!"  # You can customize this response or redirect as needed

    data = cue_and_targets[session["word_index"]]
    return render_template('semantic_similarity/drag.html', cue_word=data["cue"], target_words=data["targets"])

# Semantic Similarity pause between categories
@app.route('/semantic_similarity_pause', methods=['GET', 'POST'])
def semantic_similarity_pause():
    return render_template('semantic_similarity/pause.html')


@app.route('/similarity_save_response', methods=['POST'])
def save_response():
    selected_words = request.form.getlist('words[]')
    cue_word = request.form.getlist('cue')
    cue_word = cue_word[0] #this should only be an element, but it's a list with only one element...

    current_category = list_of_categories[session["category_index"]]
    # Retrieve the participant_id from the session
    participant_id = session.get("participant_id")
    if not participant_id:
        return jsonify(status="error", message="No participant ID found")

    entry = SemanticTask(category=current_category,participant_id=participant_id, cue_word=cue_word, selected_words=",".join(selected_words))
    db.session.add(entry)
    db.session.commit()
    print(session["word_index"])
    # Move to the next cue and target set
    session["word_index"] += 1
    print(session["category_index"])
    if session["word_index"] < len(categories[current_category]): #we should run all the members of the current category
        return jsonify(status="success", message="Data saved successfully.")
    else:
        session["category_index"] += 1 #advance category index
        session["word_index"] = 0 # restart word index
        if session["category_index"] < len(list_of_categories):
            return jsonify(status="completed", message="Category completed.")
        else:
            return jsonify(status="done", message="All categories completed.")




# reset sem index
@app.route('/reset_index')
def reset_index():
    session["word_index"] = 0
    session["category_index"] = 0
    session["word_index_feat"] = 0
    session["category_index_feat"] = 0
    return "Index reset to 0"

@app.route('/feature_rating_intro', methods=['GET', 'POST'])
def feature_rating_intro():
    return render_template('feature_rating/intro.html')




# Feature Rating Route
@app.route('/feature_rating', methods=['GET', 'POST'])
def feature_rating():
    session.setdefault("word_index_feat", 0)
    session.setdefault("category_index_feat", 0)
    current_category = list_of_categories_feat[session["category_index_feat"]]
    cue_words = categories_feat[current_category]
    current_dimensions = cat_dimensions[current_category]
    # Check if current index is out of range
    #if session["word_index_feat"] >= len(list_of_categories_feat):
     #   return "All tasks completed. Thank you!"  # You can customize this response or redirect as needed
    current_word = cue_words[session["word_index_feat"]]    
    return render_template('feature_rating/rate.html',word=current_word, dimensions=current_dimensions)

#save feature rating data
@app.route('/feature_save', methods=['POST'])
def feature_save():
    current_category = list_of_categories_feat[session["category_index_feat"]]
    cue_words = categories_feat[current_category]
    current_dimensions = cat_dimensions[current_category] #this gives you a list of two-item lists
    participant_id = session.get("participant_id")
    if participant_id is None:
        participant_id = "nones"
    current_word = cue_words[session["word_index_feat"]]
                             
    # get dimension names to retrieve rating values
    dim0 = [dim[0] for dim in current_dimensions]
    
    print(dim0)
    
    ratings = [request.form.get(x) for x in dim0]
    
    print(ratings)
    
    for dim,num in zip(dim0,ratings):
        entry = DimensionTask(category=current_category,participant_id=participant_id, cue_word=current_word, dim=dim,rating=int(num))
        db.session.add(entry)
    db.session.commit()
    
    session["word_index_feat"] += 1
    
    if session["word_index_feat"]   >= len(cue_words):
        session["word_index_feat"] = 0
        session["category_index_feat"] += 1
        if session["category_index_feat"]   >= len(list_of_categories_feat):
            return redirect(url_for('gracias'))
        return redirect(url_for('feature_pause'))
    
    return redirect(url_for('feature_rating'))


# Feature rating pause between categories
@app.route('/feature_pause', methods=['GET', 'POST'])
def feature_pause():
    return render_template('feature_rating/pause.html')



if __name__ == "__main__":
    app.run(debug=True)
