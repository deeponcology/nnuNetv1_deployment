import os

def add_dcm_extension(directory):
    # Iterate over all files in the specified directory
    for filename in os.listdir(directory):
        # Construct the full file path
        file_path = os.path.join(directory, filename)
        # Check if the file is a regular file and does not have an extension
        if os.path.isfile(file_path) and not os.path.splitext(filename)[1]:
            # New file name with .dcm extension
            new_file_path = file_path + '.dcm'
            # Rename the file
            os.rename(file_path, new_file_path)
            print(f'Renamed {file_path} to {new_file_path}')

# Replace 'path_to_your_directory' with the path to the directory containing your DICOM files
directory_path = '/Volumes/AI-Data/TCIA/LiverTumor/vip/3Dircadb1/3Dircadb1.1/MASKS_DICOM/portalvein'
add_dcm_extension(directory_path)
