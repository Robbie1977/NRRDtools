import numpy as np
import sys
import nrrd

# Check if the correct number of command-line arguments is provided
if len(sys.argv) < 4:
    print('Error: missing arguments!')
    print('e.g. python matchIndex.py indexfile.nrrd intensity(0-254) imagefile.nrrd [outputfile.csv]')
else:
    # Read the NRRD files using the command-line arguments
    data1, header1 = nrrd.read(str(sys.argv[1]))
    data2, header2 = nrrd.read(str(sys.argv[3]))

    # Initialize the result string and the delimiter
    result = "["
    div = ""

    # Check if the image sizes are the same
    if data1.size != data2.size:
        print('\n\nError: Images must be the same size!!')
    else:
        # Loop through unique values in data1
        for val in np.unique(data1):
            if val > 0:
                # Check if the maximum value in data2 for the given condition is greater than the provided intensity
                if np.max(data2[data1 == np.uint8(val)]) > np.uint8(sys.argv[2]):
                    # Add the value to the result string
                    result = result + div + str(val).zfill(2)
                    div = ", "

        # Close the result string
        result = result + "]"

        # Print the result
        print(result)

        # If an output file is provided, append the result to the file
        if len(sys.argv) > 4:
            with open(str(sys.argv[4]), "a") as myfile:
                myfile.write(str(sys.argv[1]) + ', ' + str(sys.argv[2]) + ', ' + str(sys.argv[3]) + ', ' + result + '\n')
