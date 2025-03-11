# Recursive Extraction and Build Automation Script

This script automates the process of extracting student archives, cleaning up previous build directories, and building C++ projects that contain a `Main.cpp` file.

## Features

- **Recursive Extraction:**  
  Searches through a given input directory for student archives (supported formats: `.tar.gz`, `.tgz`, and `.zip`) and extracts them while preserving the original subdirectory structure.

- **Clean Build Environment:**  
  Before building a project, the script checks for and deletes any existing `build` folder within the extracted project to ensure a clean build environment.

- **Smart Build Process:**  
  It recursively locates the directory containing `Main.cpp` within each extracted project, creates a new `build` directory there, and executes the build commands (`cmake` and `make`).

- **Logging:**  
  Uses [loguru](https://github.com/Delgan/loguru) for logging the entire build process. Additionally, the output of the build commands (both stdout and stderr) is saved in a `build.log` file in the new build directory.

- **Suppress CMake Warnings:**  
  The script passes the flag `-DCMAKE_SUPPRESS_DEVELOPER_WARNINGS=TRUE` to `cmake` to ignore deprecation and developer warnings.

## Requirements

- Python 3.x  
- [loguru](https://pypi.org/project/loguru/)  
- Standard Python libraries: `os`, `tarfile`, `zipfile`, `shutil`, `argparse`, `subprocess`

## Installation

1. **Clone or download the repository.**

2. **Install loguru:**

   ```bash
   pip install loguru

