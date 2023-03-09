import argparse
import numpy as np


def obj_centroid(obj_file):
    """
    Calculates the centroid of a mesh from an OBJ file and returns the X,Y,Z coordinates.

    Parameters:
    obj_file (str): Path to the OBJ file.

    Returns:
    centroid (tuple): A tuple containing the X,Y,Z coordinates of the centroid.
    """

    # Open the OBJ file and read the vertex data
    with open(obj_file, 'r') as f:
        vertices = []
        for line in f:
            if line.startswith('v '):
                vertex = list(map(float, line.split()[1:]))
                vertices.append(vertex)

    # Convert the vertices list to a numpy array for easier calculations
    vertices = np.array(vertices)

    # Calculate the centroid using numpy
    centroid = np.mean(vertices, axis=0)

    # Return the centroid as a tuple of floats
    return tuple(map(float, centroid))


def main():
    """
    Entry point for the script. Parses command line arguments and calls obj_centroid.
    """

    # Set up argument parser
    parser = argparse.ArgumentParser(description='Calculate the centroid of a mesh from an OBJ file.')
    parser.add_argument('obj_file', help='Path to the OBJ file.')

    # Parse arguments
    args = parser.parse_args()

    # Calculate the centroid and print the result
    centroid = obj_centroid(args.obj_file)
    print('Centroid: ({:.4f}, {:.4f}, {:.4f})'.format(*centroid))


if __name__ == '__main__':
    main()
