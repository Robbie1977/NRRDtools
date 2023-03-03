# NRRDtools

A collection of Python scripts for working with NRRD files.

- `obj_to_nrrd.py`: A Python script for converting OBJ files to binary NRRD files with a physical size of 1 micron per voxel and microns as the unit for each axis.
- `nrrd_info.py`: A Python script for printing information about NRRD files, including their size, dimensions, and metadata.
- `nrrd_viewer.py`: A Python script for visualizing NRRD files using the VTK library.
- `example.obj`: An example OBJ file that can be used with obj_to_nrrd.py.
- `example.nrrd`: An example NRRD file that can be used with nrrd_viewer.py.

## Installation

To install the package, clone the repository and install the dependencies:

```bash
git clone https://github.com/Robbie1977/NRRDtools.git
cd NRRDtools
pip install -r requirements.txt
```

### Requirements
The scripts in this repository require the following dependencies:

```
NumPy
NRRD
VTK (only required for nrrd_viewer.py)
```
You can install these dependencies using pip:

```bash
pip install numpy nrrd vtk
Usage
obj_to_nrrd.py
```

## obj_to_nrrd.py

Convert an OBJ file to a binary NRRD file with a physical size of 1 micron per voxel and microns as the unit for each axis.

### Usage

python obj_to_nrrd.py input.obj [output.nrrd] ['(X,Y,Z)'] [radius]

### Parameters

- `input_file`: str, path to the input OBJ file
- `output_file`: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '.nrrd' extension
- `extent`: tuple (optional), the extent of the voxel grid. If not specified, the extent will be calculated based on the maximum vertex coordinates in the OBJ file.
- `radius`: float (optional), the radius of the sphere of voxels to mark as True for each vector point.

## nrrd_to_obj.py

Convert a binary NRRD file to an OBJ file.

### Usage

```bash
python nrrd_to_obj.py input.nrrd [output.obj]
```

### Parameters

- `input_file`: str, path to the input NRRD file
- `output_file`: str (optional), path to the output OBJ file. If not specified, the output file will have the same name as the input file but with the '.obj' extension

## crop_nrrd.py

Crop a binary NRRD file to a specified region of interest (ROI).

### Usage

```bash
python crop_nrrd.py input.nrrd [output.nrrd] ['(X,Y,Z)'] ['(W,H,D)']
```

### Parameters

- `input_file`: str, path to the input NRRD file
- `output_file`: str (optional), path to the output NRRD file. If not specified, the output file will have the same name as the input file but with the '_cropped.nrrd' extension
- `origin`: tuple (optional), the origin of the ROI. If not specified, the ROI will start at (0,0,0)
- `size`: tuple (optional), the size of the ROI. If not specified, the size of the ROI will be the same as the size of the input file.

## nrrd_info.py

`nrrd_info.py` is a Python script that allows the user to view the header information of an NRRD file. The script takes a path to an NRRD file as an argument and then prints out the header information of the file to the console.

The script imports the nrrd module, which provides functions for reading and writing NRRD files. It then uses the nrrd.read_header() function to read the header information of the NRRD file specified by the user.

The header information is stored in a dictionary, and the script then iterates through the keys and values of the dictionary and prints them out to the console. This includes information such as the dimensions of the NRRD file, the units of measurement used, and any additional metadata that may be present in the header.

nrrd_info.py provides a convenient way for users to quickly view the header information of an NRRD file without needing to open it in a separate program.

### Usage

To use nrrd_info.py, run the following command:

```python
python nrrd_info.py input.nrrd
```

### Parameters

- input.nrrd is the path to the input NRRD file.
nrrd_viewer.py

## nrrd_viewer.py

The `nrrd_viewer.py` script in the NRRDtools repository is a simple GUI application that allows users to visualize and explore NRRD files. It is built using the PyQt5 library and leverages the matplotlib and numpy libraries for data visualization.

The main window of the application displays the axial, coronal, and sagittal views of the NRRD file. Users can interact with the displayed image by panning and zooming using the mouse or by using the built-in controls.

In addition to image visualization, the application provides basic information about the loaded NRRD file, including the dimensions, voxel size, and data type. Users can also save a screenshot of the displayed image or export the NRRD file to a different file format.

Overall, nrrd_viewer.py provides a simple and user-friendly way to view and interact with NRRD files.

### Usage

To use nrrd_viewer.py, run the following command:

```python
python nrrd_viewer.py input.nrrd
```

### Parameters

- input.nrrd is the path to the input NRRD file.


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- The NRRD file format was developed by the Scientific Computing and Imaging Institute at the University of Utah.
