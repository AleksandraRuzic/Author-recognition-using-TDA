import gudhi
import pandas as pd
import matplotlib.pyplot as plt
import os


def save_diagram(filename):

    df = pd.read_csv("../distances/our_distances/" + filename, index_col=0)
    df = df.to_numpy()
    rips_complex = gudhi.RipsComplex(distance_matrix = df)
    simplex_tree = rips_complex.create_simplex_tree(max_dimension=2)
    # simplex_tree.prune_above_filtration(20)
    diag = simplex_tree.persistence()

    # plt.figure(figsize=(10, 5))
    gudhi.plot_persistence_diagram(diag)
    plt.savefig("../diagrams/our_diagrames/" + '.'.join(filename.split('.')[:-1]) + ".png")


directory = "../distances/our_distances"

for filename in os.listdir(directory):

    if filename.endswith(".csv"):
        save_diagram(filename)

