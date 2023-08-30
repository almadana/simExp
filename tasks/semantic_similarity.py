from flask import Flask, render_template, request, redirect, url_for, flash

# ... rest of the imports ...

@app.route('/semantic_similarity_drag', methods=['GET', 'POST'])
def semantic_similarity_drag():
    cue_word = "apple"  # Example, can be randomized or fetched
    target_words = ["banana", "cherry", "grape", "bone","park","pork","dong"]  # and so on up to 20 words or so.

    if request.method == 'POST':
        selected_words = request.form.get('selected_words', '').split(',')
        # Now you have selected words as a list. You can store it or process it as required.
        flash("Selected words saved successfully!")  # Feedback for the user
        return redirect(url_for('semantic_similarity_drag'))

    return render_template('semantic_similarity_drag.html', cue_word=cue_word, target_words=target_words)
