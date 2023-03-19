import sys

def print_obj_max_extents(file_path):
    """
    Print the maximum extents of an OBJ file.

    :param file_path: str, path to the OBJ file
    """
    max_coords = [float('-inf'), float('-inf'), float('-inf')]
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                coords = [float(x) for x in line.strip().split()[1:]]
                max_coords = [max(max_coords[i], coords[i]) for i in range(3)]
    print('Max extents of {}: {}'.format(file_path, max_coords))

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python <script_name.py> <obj_file_path>')
    else:
        file_path = sys.argv[1]
        print_obj_max_extents(file_path)
