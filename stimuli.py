# STIMULI SORTER

import numpy.random as rand
import json
import os


json_file_emo = "static/data/cat_emo.json"

json_file_emo_dims = "static/data/dimensions.json"

# load data into dicts

def load_json(base_dir,jsonfile):
    with open(os.path.join(base_dir,jsonfile)) as jsonf:
        return json.load(jsonf)


# sortea n_cats categorias de la lista completa, y la devuelve en un dict
#devuelve un diccionario
def get_cats(n_cats = 3,base_dir="./"):
    emo_cats = load_json(base_dir,json_file_emo)
    keys = list(emo_cats.keys())
    rand_keys = [keys[i] for i in rand.permutation(len(keys)) ]
    return {key: emo_cats[key] for key in rand_keys[:n_cats]}


def dim_split(list):
    return( [x.split("/") for x in list] )

def get_dimensions(selected_cats,base_dir):
    dimensions = load_json(base_dir,json_file_emo_dims)
    cats = list(selected_cats.keys())
    selected_dims = [dim_split(dimensions[i]) for i in cats]
    return {key: sd for key,sd in zip(cats,selected_dims)}


#toma un diccionario, genera un diccionario (claves: categorías) de lista de diccionarios, con claves cue: y targets;
def gen_cue_cats(cats):
    stim = {}
    #for each category
    for this_cat in cats.keys():
        #list of all the words in the cat
        cue_words = cats[this_cat]
        #this list will contain all the dictionaries for this category
        trial_list=[]
        for this_word in cue_words:
            other_words = [word for word in cue_words if word not in this_word]
            other_words = [other_words[i] for i in rand.permutation(len(other_words))] #randomize the order of appereance of target words
            trial_list.append({"cue": this_word, "targets": other_words})
        #randomize the order of appearance of cues in category
        trial_list = [trial_list[i] for i in rand.permutation(len(trial_list))]
        stim[this_cat] = trial_list
    return stim

#def get_cat_dims
