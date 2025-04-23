def find_bounding_box(file_path=None, file_content=None):
    """
    Find the bounding box (min and max XYZ coordinates) for an OBJ or SWC file
    
    Parameters:
    -----------
    file_path : str, optional
        Path to the OBJ or SWC file
    file_content : str, optional
        The content of the OBJ or SWC file as a string
        
    Returns:
    --------
    dict
        A dictionary containing min and max points of the bounding box
        Format: {'min': {'x': min_x, 'y': min_y, 'z': min_z},
                 'max': {'x': max_x, 'y': max_y, 'z': max_z}}
    
    Raises:
    -------
    ValueError
        If neither file_path nor file_content is provided,
        if the file format is not recognized,
        or if no valid coordinates are found
    
    Note:
    -----
    Either file_path or file_content must be provided
    """
    if file_path is None and file_content is None:
        raise ValueError("Either file_path or file_content must be provided")
    
    # Initialize min and max with extreme values
    min_x, min_y, min_z = float('inf'), float('inf'), float('inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    coordinates_found = False
    
    # Determine file type
    is_obj = False
    is_swc = False
    
    # If file_path is provided, determine file type from extension first
    if file_path:
        file_extension = file_path.lower().split('.')[-1]
        is_obj = file_extension == 'obj'
        is_swc = file_extension == 'swc'
    
    # Process the file/content based on its type
    if file_content:
        lines = file_content.strip().split('\n')
    else:  # file_path is provided
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Try opening as binary for potential non-text files
            with open(file_path, 'rb') as f:
                lines = [line.decode('utf-8', errors='ignore') for line in f.readlines()]
    
    # If file type couldn't be determined from extension, check content
    if not (is_obj or is_swc):
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if line.startswith('v '):
                is_obj = True
                break
            parts = line.split()
            if len(parts) >= 7 and not line.startswith('#'):
                try:
                    int(parts[0])
                    float(parts[2])
                    is_swc = True
                    break
                except ValueError:
                    continue
    
    # Process lines based on file type
    if is_obj:
        # Process OBJ file
        for line in lines:
            line = line.strip()
            # We're only interested in vertex positions (lines starting with 'v ')
            if line.startswith('v '):
                parts = line.split()
                # OBJ vertex lines should have at least 4 parts: 'v', x, y, z
                if len(parts) >= 4:
                    try:
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        
                        # Update bounding box
                        min_x = min(min_x, x)
                        min_y = min(min_y, y)
                        min_z = min(min_z, z)
                        
                        max_x = max(max_x, x)
                        max_y = max(max_y, y)
                        max_z = max(max_z, z)
                        
                        coordinates_found = True
                    except ValueError:
                        # Skip lines with invalid numbers
                        continue
    
    elif is_swc:
        # Process SWC file
        for line in lines:
            line = line.strip()
            # Skip comment lines (starting with #)
            if line.startswith('#') or not line:
                continue
            
            parts = line.split()
            # SWC lines should have 7 columns (index, type, x, y, z, radius, parent)
            if len(parts) >= 7:
                try:
                    # In SWC, columns 3-5 are x, y, z coordinates (0-indexed)
                    x, y, z = float(parts[2]), float(parts[3]), float(parts[4])
                    
                    # Update bounding box
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    min_z = min(min_z, z)
                    
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                    max_z = max(max_z, z)
                    
                    coordinates_found = True
                except ValueError:
                    # Skip lines with invalid numbers
                    continue
    
    else:
        error_msg = 'File format not recognized as OBJ or SWC'
        if file_path:
            error_msg += f': {file_path}'
        raise ValueError(error_msg)
    
    # Check if we found any valid coordinates
    if not coordinates_found:
        error_msg = 'No valid coordinates found in the file'
        if file_path:
            error_msg += f': {file_path}'
        raise ValueError(error_msg)
    
    # Create and return the bounding box
    bounding_box = {
        'min': {'x': min_x, 'y': min_y, 'z': min_z},
        'max': {'x': max_x, 'y': max_y, 'z': max_z}
    }
    
    return bounding_box


# Example usage:
if __name__ == "__main__":
    # Example with file path
    # bb = find_bounding_box(file_path="path/to/your/model.obj")
    
    # Example with file content
    obj_content = """
    # Example OBJ file
    v 1.0 2.0 3.0
    v -1.5 0.5 2.0
    v 0.0 -3.0 1.0
    v 2.5 1.0 -2.0
    f 1 2 3
    f 1 3 4
    """
    
    bb = find_bounding_box(file_content=obj_content)
    print("Bounding Box:")
    print(f"Min: ({bb['min']['x']}, {bb['min']['y']}, {bb['min']['z']})")
    print(f"Max: ({bb['max']['x']}, {bb['max']['y']}, {bb['max']['z']})")