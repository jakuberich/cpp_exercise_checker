# Recursive Extraction and Build Automation Script

This Python script automates the process of extracting student submission archives, cleaning up their directory structure, and building C++ projects. It is designed to handle common issues in student submissions, such as extra nested folders, whitespace in file and folder names, and redundant folder names containing the substring `_assignsubmission_file`.

## Features

- **Recursive Extraction:**  
  Recursively scans a specified input directory for archives (`.tar.gz`, `.tgz`, and `.zip`) and extracts them.

- **Directory Structure Cleaning:**  
  After extraction, the script:
  - **Flattens unnecessary nesting:** Removes extra single-folder wrappers.
  - **Removes whitespace:** Renames files and directories to eliminate spaces.
  - **Removes redundant folder names:** Strips out the `_assignsubmission_file` substring from folder names to reduce extra nesting.

- **Project Building:**  
  Searches for the directory containing `Main.cpp` in each extracted project. Once found, it:
  - Deletes any existing `build` folder.
  - Creates a new `build` folder.
  - Runs `cmake` and `make` to build the project.
  - Captures and logs the output (with specific filtering of a known CMake deprecation warning) to a `build.log` file within the build folder.

- **Logging:**  
  Uses [loguru](https://github.com/Delgan/loguru) for logging key events and errors. Build command outputs are recorded in a log file.

## Requirements

- Python 3.x
- [loguru](https://pypi.org/project/loguru/)
- Standard Python libraries: `os`, `tarfile`, `zipfile`, `shutil`, `argparse`, `subprocess`

## Installation

1. **Clone or download the repository.**

2. **Install the required package:**
   ```bash
   pip install loguru
   ```

## Usage

Run the script from the command line by specifying the input directory (containing student archives) and the output directory (where cleaned and extracted projects will be placed). For example:

```bash
python3 untar_and_make.py /path/to/archives /path/to/output
```

### Example

- **Input Directory Structure:**
  ```
  /path/to/archives/Name Surname_12345678_assignsubmission_file/9Surnamep.tar.gz
  /path/to/archives/student2/assignment.tar.gz
  ```

- **Output Directory Structure:**  
  For an archive in `Name Surname_12345678_assignsubmission_file`, the script will:
  - Remove whitespace (e.g., `"Name Surname_12345678"` becomes `NameSurname_12345678`).
  - Remove the redundant `_assignsubmission_file` substring.
  - Flatten extra nested folders (e.g., remove the `cpp2025/lab01/` level if it only contains the project files).

  Resulting in an output similar to:
  ```
  /path/to/output/Name_Surname_12345678/
  ```

## How It Works

1. **Extraction:**  
   The script extracts each archive into a corresponding directory in the output folder while preserving the original subdirectory structure (after cleaning).

2. **Directory Cleaning:**  
   Post-extraction, the script:
   - Flattens unnecessary single-folder wrappers.
   - Renames files and directories to remove whitespace.
   - Removes extra folder layers that contain the `_assignsubmission_file` substring.

3. **Build Process:**  
   The script searches recursively for the directory containing `Main.cpp`. When found, it:
   - Deletes any pre-existing `build` folder.
   - Creates a new `build` folder.
   - Executes `cmake` (with filtering of a specific deprecation warning) and `make` in that folder.
   - Logs the command outputs (both stdout and stderr) to a `build.log` file.

4. **Logging:**  
   Key events and errors are logged to the console via loguru, and detailed build logs are saved in the new build folder.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.