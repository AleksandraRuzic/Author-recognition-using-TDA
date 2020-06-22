from sklearn import manifold
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import gudhi

df1 = pd.read_csv("../distances/their_distances/JaneAusten_Emma_t0.csv", index_col=0)
df = df1.to_numpy()
likovi = list(df1.columns)

# Making Rips simplicial complex
rc = gudhi.RipsComplex(distance_matrix=df, max_edge_length=0.005)
st = rc.create_simplex_tree(max_dimension=2)

# We are only going to plot the triangles, edges and points
triangles = np.array([s[0] for s in st.get_skeleton(2) if len(s[0]) == 3])
duzi = np.array([s[0] for s in st.get_skeleton(1) if len(s[0]) == 2])
tacke = np.array([s[0] for s in st.get_skeleton(0) if len(s[0]) == 1])
print(triangles)
print()
print(duzi)
print()
print(tacke)

# Making 3D coordinates out of distance matrix
mds = manifold.MDS(n_components=3, dissimilarity="precomputed", random_state=6)
results = mds.fit(df)
coords = results.embedding_

fig = plt.figure()
ax = fig.gca(projection='3d')

# Ploting points and naming them
plt.scatter(coords[:, 0], coords[:, 1], coords[:, 2])
for label, x, y, z in zip(likovi, coords[:, 0], coords[:, 1], coords[:, 2]):
    ax.text(x, y, z, label)

# Ploting edges
if 0 != len(duzi):
    points = np.array(coords)
    edges = np.array(duzi)
    x = points[:, 0].flatten()
    y = points[:, 1].flatten()
    z = points[:, 2].flatten()
    for i in range(len(edges)):
        ax.plot(x[edges[i, :]], y[edges[i, :]], z[edges[i, :]])
    # ax.plot_wireframe(X=x[edges.T], Y=y[edges.T], Z=z[edges.T])

# Ploting triangles
if 0 != len(triangles):
    ax.plot_trisurf(coords[:, 0], coords[:, 1], coords[:, 2], triangles=triangles)

plt.show()
