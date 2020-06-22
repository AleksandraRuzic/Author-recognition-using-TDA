import os
import pandas as pd
import copy
import ot


# Returns Wasserstein distance between two characters in a novel
# Arguments: character1, character2 (list of integers), novelLength (integer), t (float)
def distance(character1, character2, novelLength, t):

    character1 = copy.deepcopy(character1)
    character2 = copy.deepcopy(character2)

    # First character needs to have more appearances
    if len(character1) < len(character2):
        tmp = character1
        character1 = character2
        character2 = tmp

    character1new = []
    used_list = []

    j_nearest = None

    # Find a subset of appearances of the first character so that the first character is as close as possible to the
    # second character
    for i in range(len(character2)):

        min_distance = float('inf')

        for j in range(len(character1)):

            curr_distance = abs(character1[j] - character2[i])

            if curr_distance < min_distance and j not in used_list:

                min_distance = curr_distance
                j_nearest = j

        character1new.append(character1[j_nearest])
        used_list.append(j_nearest)

    character1new.sort()

    # Normalize character appearances by dividing them with novel length
    for i in range(len(character1new)):
        character1new[i] /= novelLength
        character2[i] /= novelLength

    # Raise elements to the power of 1 + t
    for i in range(len(character1new)):
        character1new[i] **= (1+t)

    for i in range(len(character1new)):
        character2[i] **= (1+t)

    return ot.wasserstein_1d(character1new, character2, p=0.5)


# Calculates distance matrices of ten most frequent characters in a novel and writes them to csv files
# Arguments: filename (string)
def topTenCharacters(filename):

    indexes = pd.read_csv("../indexes/" + filename, header=None)
    indexes.columns = ["position", "name"]
    indexes["name"] = indexes["name"].str.lower()
    novel_length = max(indexes["position"])

    # Find ten most frequent names and find all of their appearances
    topTenNames = indexes.groupby(["name"]).size().reset_index(name="Count").sort_values('Count', axis=0, ascending=False).iloc[:10]["name"].tolist()
    indexes = indexes[indexes["name"].isin(topTenNames)]

    # Distance matrices for 3 different t parameters (0, 0.1 and -0.1)
    distances_t0 = [[0 for col in range(10)] for row in range(10)]
    distances_tminus1 = [[0 for col in range(10)] for row in range(10)]
    distances_tplus1 = [[0 for col in range(10)] for row in range(10)]

    # Save appearance positions for each of the ten characters
    characters = []
    for i in range(10):
        characters.append(indexes[indexes["name"] == topTenNames[i]]["position"].tolist())

    # Calculate the distance between every two characters save them in distances matrices
    for i in range(9):
        for j in range(i+1, 10):
            distances_t0[i][j] = distance(characters[i], characters[j], novel_length, 0)
            distances_tminus1[i][j] = distance(characters[i], characters[j], novel_length, -0.1)
            distances_tplus1[i][j] = distance(characters[i], characters[j], novel_length, 0.1)
            distances_t0[j][i] = distances_t0[i][j]
            distances_tminus1[j][i] = distances_tminus1[i][j]
            distances_tplus1[j][i] = distances_tplus1[i][j]

    # Make data frames from distance matrices and save them to csv files
    distances_t0 = pd.DataFrame(distances_t0, index=topTenNames, columns=topTenNames)
    distances_tminus1 = pd.DataFrame(distances_tminus1, index=topTenNames, columns=topTenNames)
    distances_tplus1 = pd.DataFrame(distances_tplus1, index=topTenNames, columns=topTenNames)
    distances_t0.to_csv("../distances/our_distances/" + '.'.join(filename.split('.')[:-1]) + "_t0.csv")
    distances_tminus1.to_csv("../distances/our_distances" + '.'.join(filename.split('.')[:-1]) + "_tminus1.csv")
    distances_tplus1.to_csv("../distances/our_distances" + '.'.join(filename.split('.')[:-1]) + "_tplus1.csv")


directory = "../indexes"

# Loop through all csv files in the folder indexes
for filename in os.listdir(directory):

    if filename.endswith(".csv"):
        topTenCharacters(filename)
