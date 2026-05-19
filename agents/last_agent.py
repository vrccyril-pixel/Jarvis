import os

# Set the directory path and the output file name
directory = "D:\\"
output_file = "file_list.txt"

# Get the list of files in the directory
files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

# Write the list to a text file
with open(output_file, 'w') as f:
    for file in files:
        f.write(file + "\n")

print("File list saved to:", output_file)