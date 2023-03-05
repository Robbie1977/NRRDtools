def convert_obj_to_micrometers(input_file, output_file=None):
    """
    Convert an OBJ file with vertex coordinates in nanometers to micrometers.

    :param input_file: str, path to the input OBJ file
    :param output_file: str (optional), path to the output OBJ file. If not specified, the output file will have the same name as the input file but with the '_um.obj' extension
    """
    import os
    
    # Check if output file path is specified. If not, use the default output file name
    if output_file is None:
        output_file = os.path.splitext(input_file)[0] + '_um.obj'

    # Load vertex data from OBJ file
    vertices = []
    with open(input_file, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertex = [float(x) / 1000.0 for x in line.strip().split()[1:]] # convert nanometers to micrometers
                vertices.append(vertex)
            else:
                # copy all non-vertex lines to the output file
                with open(output_file, 'a') as out_file:
                    out_file.write(line)

    # Save the converted vertex data to the output OBJ file
    with open(output_file, 'a') as out_file:
        for vertex in vertices:
            out_file.write('v {} {} {}\n'.format(vertex[0], vertex[1], vertex[2]))
            
    print('Converted vertex coordinates from nanometers to micrometers and saved to ' + output_file)


if __name__ == '__main__':
    import sys
    # Check for correct number of arguments
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print('Usage: python main.py input_file.obj [output_file.obj]')
        sys.exit(1)

    # Parse input and output file paths
    input_file = sys.argv[1]
    if len(sys.argv) == 3:
        output_file = sys.argv[2]
    else:
        output_file = None

    # Convert OBJ file from nanometers to micrometers
    convert_obj_to_micrometers(input_file, output_file)
