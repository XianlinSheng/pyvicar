import numpy as np
import stl


# map: originallist -> newlist
def reduce_vertex(vertices, tol=1e-10):
    new_vertex = []
    new_map = []
    # sort order 0,1,2
    sort_map = np.lexsort((vertices[:, 2], vertices[:, 1], vertices[:, 0]))

    new_vertex.append(vertices[sort_map[0], :])
    bounding_box = np.array(
        [vertices[sort_map[0], :], vertices[sort_map[-1], :]]
    )  # init bounding box from x0, y0, z0 to xn, yn, zn
    new_map.append(0)
    prev_index = sort_map[0]
    for index in sort_map[1:]:
        # if not the same, define a new vertex
        if np.linalg.norm(vertices[index, :] - vertices[prev_index, :]) > tol:
            new_vertex.append(vertices[index, :])
            # axis 0 is already sorted
            if vertices[index, 1] < bounding_box[0, 1]:
                bounding_box[0, 1] = vertices[index, 1]
            if vertices[index, 1] > bounding_box[1, 1]:
                bounding_box[1, 1] = vertices[index, 1]
            if vertices[index, 2] < bounding_box[0, 2]:
                bounding_box[0, 2] = vertices[index, 2]
            if vertices[index, 2] > bounding_box[1, 2]:
                bounding_box[1, 2] = vertices[index, 2]

        # map sortedoriginallist -> newlist
        new_map.append(len(new_vertex) - 1)
        prev_index = index

    new_vertex = np.array(new_vertex, dtype=float)

    # map originallist -> sortedoriginallist
    inverse_map_dict = {sort_map[i]: i for i in range(len(sort_map))}
    inverse_map = np.array(
        [inverse_map_dict[index] for index in range(len(sort_map))], dtype=int
    )

    # map originallist -> sortedoriginallist -> newlist
    new_map = np.array(new_map, dtype=int)
    new_map = new_map[inverse_map]

    return new_vertex, new_map, bounding_box


def read_stl(path, tol=1e-10):
    mesh = stl.mesh.Mesh.from_file(path)

    # [
    #     x1, y1, z1; for face1
    #     x2, y2, z2;
    #     x3, y3, z3;
    #
    #     x1, y1, z1; for face2
    #     x2, y2, z2;
    #     x3, y3, z3;
    #
    #     ...
    # ]
    vertices = mesh.vectors
    face_n = vertices.shape[0]
    vertices = vertices.reshape((-1, 3))

    # merge same vertex definition
    vertices, vertex_map, bounding_box = reduce_vertex(vertices, tol)

    # Update element list based on the new indices
    elements = np.array(
        [
            [vertex_map[3 * i], vertex_map[3 * i + 1], vertex_map[3 * i + 2]]
            for i in range(face_n)
        ],
        dtype=int,
    )
    elements = elements[np.lexsort((elements[:, 2], elements[:, 1], elements[:, 0]))]

    return vertices, elements, bounding_box
