class FeatureRatingForm(FlaskForm):
    good_bad = IntegerField('Good-Bad Rating')
    heavy_light = IntegerField('Heavy-Light Rating')
    submit = SubmitField('Submit')

@app.route('/feature_rating', methods=['GET', 'POST'])
def feature_rating():
    form = FeatureRatingForm()
    word = "rock"  # Example, can be randomized or fetched
    if form.validate_on_submit():
        good_bad_rating = form.good_bad.data
        heavy_light_rating = form.heavy_light.data
        # Store ratings
        return redirect(url_for('index'))
    return render_template('feature_rating.html', form=form, word=word)
