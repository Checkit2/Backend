from rapidfuzz import fuzz
import operator

"""
    this function return similar value for given string with given dataset
    first returned value will be similar word
    seccond value is accuracy
"""
def find_similar(search_for, dataset):
    res = []
    for data in dataset:
        res.append(fuzz.ratio(search_for, data))
    i, v = max(enumerate(res), key=operator.itemgetter(1))
    yield dataset[i]
    yield v


dataset = [ "Appereance",
            "color",
            "Specifie Gravity",
            "PH",
            "Protein",
            "Glucose",
            "Keton",
            "Blood",
            "Bilirubin",
            "Urobilinogen",
            "Nitrite",
            "RBC/hpf",
            "WBC/hpf",
            "Epithelial cells/Lpf",
            "EC/Lpf",
            "Bacteria",
            "Casts",
            "Mucous"]


"""

color yellow
asjdhaj askfjkas fsfkajfk

\n
 

"""



word, accuracy = find_similar("nitrte", dataset)
print("Given word -> ", "nitrte")
print("result ->")
print(word, accuracy)