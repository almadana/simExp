import csv, json

def make_json(csv_filepath, json_filepath):

    data=dict()

    with open(csv_filepath,encoding="utf-8") as csvf:
        csvReader = csv.reader(csvf)

        for rows in csvReader:

            key = rows.pop(0)
            print(key)
            print(rows)
            data[key] = rows

    with open(json_filepath, 'w', encoding = "utf-8") as jsonf:
        jsonf.write(json.dumps(data,indent=4))




csv_filepath = "static/data/cat_emo.csv"
json_filepath = "static/data/cat_emo.json"

make_json(csv_filepath,json_filepath)


csv_filepath = "static/data/dimensions.csv"
json_filepath = "static/data/dimensions.json"

make_json(csv_filepath,json_filepath)
