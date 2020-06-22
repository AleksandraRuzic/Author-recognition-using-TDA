import os
from random import sample

import pandas as pd
import numpy as np
from ripser import Rips
from gudhi.hera import wasserstein_distance
import gudhi


# Takes filename of a distance file and makes a simplex tree. Returns components and loops pair.
def create_rips_diag(file):
    dist = pd.read_csv("../distances/our_distances/" + file, index_col=0)
    dist = dist.to_numpy()
    rips_complex = gudhi.RipsComplex(distance_matrix=dist)
    simplex_tree = rips_complex.create_simplex_tree(max_dimension=2)
    # simplex_tree.prune_above_filtration(20)
    diag = simplex_tree.persistence()
    list0 = []
    list1 = []
    for d in diag:
        if d[0] == 0:
            list0.append(d[1])
        elif d[0] == 1:
            list1.append(d[1])
    matrix0 = []
    for l in list0:
        if l[1] == float("inf"):
            matrix0.append([l[0], 1])
        else:
            matrix0.append([l[0], l[1]])
    matrix1 = []
    for l in list1:
        if l[1] == float("inf"):
            matrix1.append([l[0], 1])
        else:
            matrix1.append([l[0], l[1]])

    return [matrix0, matrix1]


# Takes a dataframe that represents distance matrix of novels of two authors, performs a KNN with NFold
# cross validation and returns the accuracy of the classification
# Arguments: distance_novels (dataframe)
def acc_for_writers(distance_novels, num_of_folds, num_of_neighbors):

    # Shuffle rows, add prediction column, find size of one fold and get the names of writers
    new_dist_novels = distance_novels.sample(frac=1)
    new_dist_novels["prediction"] = new_dist_novels["writer"]
    size_of_fold = int(np.ceil(new_dist_novels.shape[0] / num_of_folds))
    writers = distance_novels["writer"].unique()

    # Loop through folds
    for ind in range(0, num_of_folds):

        # Split data frame into test and training sets
        if ind == num_of_folds - 1:
            test = new_dist_novels.iloc[ind * size_of_fold:]
            training = new_dist_novels.drop(new_dist_novels.index[ind * size_of_fold:])
        else:
            test = new_dist_novels.iloc[ind * size_of_fold:(ind + 1) * size_of_fold]
            training = new_dist_novels.drop(new_dist_novels.index[ind * size_of_fold:(ind + 1) * size_of_fold])

        # Loop through indexes of the test set (novel names of the test set)
        for index in test.index:

            # Find the closest novels to the current novel and calculate their frequencies
            neighbors = training.sort_values(by=index, ascending=True).iloc[:num_of_neighbors]
            neighbors["freq"] = 1 / neighbors[index] ** 2

            # Predict the author of the novel using sum of frequencies of the closest novels
            writer0 = neighbors[neighbors["writer"] == writers[0]].sum()["freq"]
            writer1 = neighbors[neighbors["writer"] == writers[1]].sum()["freq"]
            if writer0 > writer1:
                new_dist_novels.at[index, "prediction"] = writers[0]
            else:
                new_dist_novels.at[index, "prediction"] = writers[1]

    return np.sum(new_dist_novels["prediction"] == new_dist_novels["writer"]) / new_dist_novels.shape[0]


directory = "../distances/our_distances"
files_t0 = []
files_tminus = []
files_tplus = []
authors_novels = {}
novel_names = []

# Loop through csv files in distances folder and save them in t0, tminus and tplus lists
for filename in os.listdir(directory):

    if filename.endswith("_t0.csv"):
        files_t0.append(filename)
        # Save the names and the authors of the novels
        tmp = filename.split("_")
        if tmp[0] not in authors_novels:
            authors_novels[tmp[0]] = set()
            authors_novels[tmp[0]].add(tmp[1])
        else:
            authors_novels[tmp[0]].add(tmp[1])
        novel_names.append(tmp[1])
    elif filename.endswith("_tminus1.csv"):
        files_tminus.append(filename)
    elif filename.endswith("_tplus1.csv"):
        files_tplus.append(filename)

rips_diagram_t0 = []
rips_diagram_tminus = []
rips_diagram_tplus = []
rips = Rips()

# Calculate rips diagrams for every distance matrix
for i in range(0, len(files_t0)):
    rips_diagram_t0.append(create_rips_diag(files_t0[i]))
    rips_diagram_tminus.append(create_rips_diag(files_tminus[i]))
    rips_diagram_tplus.append(create_rips_diag(files_tplus[i]))

# Make a distance matrix between all pairs of novels using wasserstein distance on the Rips diagrams
dist_novels = pd.DataFrame(index=novel_names, columns=novel_names)
for i in range(0, len(novel_names)):
    """novel0_len = max(pd.read_csv("../indexes/" + files_t0[i][:files_t0[i].rfind("_")] + ".csv",
                                 names=["position", "name"], header=None)["position"])"""
    for j in range(i + 1, len(novel_names)):
        """novel1_len = max(pd.read_csv("../indexes/" + files_t0[j][:files_t0[j].rfind("_")] + ".csv",
                                     names=["position", "name"], header=None)["position"])"""

        diag0_components = np.array(rips_diagram_t0[i][0])
        diag1_components = np.array(rips_diagram_t0[j][0])
        diag0_loops = np.array(rips_diagram_t0[i][1])
        diag1_loops = np.array(rips_diagram_t0[j][1])
        t0 = wasserstein_distance(diag0_components, diag1_components, order=1.0) + wasserstein_distance(diag0_loops, diag1_loops, order=1.0)

        diag0_components = np.array(rips_diagram_tminus[i][0])
        diag1_components = np.array(rips_diagram_tminus[j][0])
        diag0_loops = np.array(rips_diagram_tminus[i][1])
        diag1_loops = np.array(rips_diagram_tminus[j][1])
        tminus = wasserstein_distance(diag0_components, diag1_components, order=1.0) + wasserstein_distance(diag0_loops, diag1_loops, order=1.0)

        diag0_components = np.array(rips_diagram_tplus[i][0])
        diag1_components = np.array(rips_diagram_tplus[j][0])
        diag0_loops = np.array(rips_diagram_tplus[i][1])
        diag1_loops = np.array(rips_diagram_tplus[j][1])
        tplus = wasserstein_distance(diag0_components, diag1_components, order=1.0) + wasserstein_distance(diag0_loops, diag1_loops, order=1.0)

        dist_novels.at[novel_names[i], novel_names[j]] = t0 ** 2 + tminus ** 2 + tplus ** 2
        dist_novels.at[novel_names[j], novel_names[i]] = dist_novels.at[novel_names[i], novel_names[j]]

for i in range(0, len(novel_names)):
    dist_novels.at[novel_names[i], novel_names[i]] = 0

authors = list(authors_novels.keys())
acc_authors = pd.DataFrame(index=authors, columns=authors)

# Calculate the accuracy between every two authors by calling classification function 200 times
for num_of_folds in range(6, 11):
    for num_of_neighbors in range(3, 6):
        if num_of_neighbors == 3 and num_of_folds == 6:
            continue
        for i in range(0, len(authors) - 1):
            for j in range(i + 1, len(authors)):

                # Take equal number of novels of both authors by sampling novels of the author who has more novels
                a1 = list(authors_novels[authors[i]])
                a2 = list(authors_novels[authors[j]])
                avg_acc = 0.0
                for k in range(0, 200):
                    if len(a1) > len(a2):
                        a1 = sample(a1, len(a2))
                    elif len(a1) < len(a2):
                        a2 = sample(a2, len(a1))
                    novel_list = a1 + a2
                    # Take only the part of distance matrix of novels that applies for this pair of authors
                    df = dist_novels[novel_list].loc[novel_list]
                    df.at[a1, "writer"] = authors[i]
                    df.at[a2, "writer"] = authors[j]
                    avg_acc = avg_acc + acc_for_writers(df, num_of_folds, num_of_neighbors)
                acc_authors.at[authors[i], authors[j]] = avg_acc / 200
                acc_authors.at[authors[j], authors[i]] = acc_authors.at[authors[i], authors[j]]

        for i in range(0, len(authors)):
            acc_authors.at[authors[i], authors[i]] = 1
        acc_authors.to_csv("../results/dist_norm/accuracy_" + str(num_of_folds) + "folds_" + str(num_of_neighbors) + "neighbors.csv")

#print(acc_authors.to_string())
