import sys
import numpy as np

# Check if the correct number of command-line arguments is provided
if len(sys.argv) < 2:
    print('Error: missing arguments!')
    print('e.g. python modSWC.py neuron.swc')
else:
    # Read the lines from the input file
    lines = [line.strip() for line in open(str(sys.argv[1]))]

    out = []

    for line in lines:
        if '#' not in line:
            # Split the line into values
            values = line.split(' ')

            # Convert the nanometer units to microns
            values[2] = str(np.divide(np.double(values[2]), 125.0))
            values[3] = str(np.divide(np.double(values[3]), 125.0))
            values[4] = str(np.divide(np.double(values[4]), 125.0))

            if np.double(values[5]) > 0:
                values[5] = str(np.divide(np.double(values[5]), 125.0))
                if np.int(values[0]) == 1 and np.int(values[1]) == 0:
                    values[1] = str(np.int(1))

            # Append the modified line to the output list
            out.append(' '.join(values))
        else:
            # Add comments to the output list, with a special case for the 'Created by' line
            if 'Created by' not in line:
                out.append(line)
            else:
                out.append(line + '; Scaled to microns (1/125) by https://github.com/Robbie1977/NRRDtools/blob/master/modHemiBrainSWC.py')

    # Write the output to the input file, overwriting its contents
    with open(str(sys.argv[1]), "w") as file_object:
        file_object.writelines('\n'.join(out))

    print('Converted {}'.format(str(sys.argv[1])))
