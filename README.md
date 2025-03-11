
# Recursive Extraction, Build Automation, and Assignment Check Automation

This repository contains two Python scripts designed to automate the evaluation of student C++ assignments. The first script extracts student submission archives, cleans and flattens their directory structure, and builds the projects using CMake and Make. The second script runs additional checks on the built projects by parsing build logs and executing Valgrind to detect memory issues, then compiles the results into a consolidated CSV report.

---

## Programs

### 1. Extraction and Build Automation Script

**Script Name:** `untar_and_make.py`

This script automates the following steps:

- **Recursive Extraction:**  
  It scans a specified input directory for archives (`.tar.gz`, `.tgz`, and `.zip`) and extracts them.

- **Directory Structure Cleaning:**  
  After extraction, the script:
  - **Flattens unnecessary nesting:** Removes extra single-folder wrappers.
  - **Removes whitespace:** Renames files and directories to eliminate spaces.
  - **Removes redundant folder names:** Strips out the `_assignsubmission_file` substring from folder names to reduce extra nesting.

- **Project Building:**  
  It recursively searches for the directory containing `Main.cpp` in each extracted project. Once found, it:
  - Deletes any existing `build` folder.
  - Creates a new `build` folder.
  - Executes `cmake` (with filtering of a known deprecation warning) and `make` in that folder.
  - Captures and logs the output to a `build.log` file within the build folder.

- **Logging:**  
  Uses [loguru](https://github.com/Delgan/loguru) to log key events and errors. All command outputs are recorded in log files.

### 2. Assignment Check Automation Script

**Script Name:** `check_assignments.py`

This script is intended to run after the build process. It performs the following actions for each built project:

- **Build Log Analysis:**  
  Parses the `build.log` file to count compilation errors and warnings using a simple heuristic.

- **Executable Detection:**  
  Searches the project's build folder for an executable file.

- **Valgrind Memory Check:**  
  Runs Valgrind (with full leak-check) on the executable and writes its output to `valgrind.log`.  
  It then parses the Valgrind output to extract the "ERROR SUMMARY" line and determine if there are any memory issues.

- **Report Generation:**  
  Collects the following information for each project into a CSV report:
  - Project name.
  - Number of compilation errors and warnings.
  - Compilation status.
  - A flag indicating if the build failed (e.g. due to compilation errors or missing executable).
  - Path to the executable (if found).
  - Valgrind status (e.g. "OK", "Memory issues", "Valgrind Error", or "No executable found").
  - The full error summary from Valgrind (if available).

---

## Requirements

- **Python:** 3.x  
- **Packages:**
  - [loguru](https://pypi.org/project/loguru/)
  - [pandas](https://pandas.pydata.org/) (for the check script)
- **Standard Python libraries:** `os`, `tarfile`, `zipfile`, `shutil`, `argparse`, `subprocess`
- **Build Tools:** CMake and Make must be installed.
- **Valgrind:** Installed on your system (ensure that necessary debug symbol packages are installed for your system).

---

## Installation

1. **Clone or download the repository.**

2. **Install Python dependencies:**

   ```bash
   pip install loguru pandas / conda install conda-forge::loguru conda-forge::pandas
   ```
---

## Usage

### Step 1: Extraction and Build

Run the first script to extract and build all student projects:

```bash
python3 untar_and_make.py /path/to/archives /path/to/output
```

- **Input Directory Structure Example:**
  ```
  /path/to/archives/Name Surname_12345678_assignsubmission_file/9Surnamep.tar.gz
  /path/to/archives/student2/assignment.tar.gz
  ```

- **Output Directory Structure:**  
  For an archive in `Name Surname_12345678_assignsubmission_file`, the script will:
  - Remove whitespace (e.g., `"Name Surname_12345678"` becomes `Name_Surname_12345678`).
  - Remove the redundant `_assignsubmission_file` substring.
  - Flatten extra nested folders.
  
  The final output might resemble:
  ```
  /path/to/output/Name_Surname_12345678/
  ```

### Step 2: Assignment Check

Once all projects are built, run the second script to perform additional checks and generate a report:

```bash
python3 check_assignments.py /path/to/output --report report.csv
```

This will generate a CSV file (`report.csv` by default) containing detailed information for each project regarding:
- Compilation errors and warnings.
- Build success or failure.
- Valgrind memory check status and detailed error summary.

---

## How It Works

1. **Extraction:**  
   The extraction script scans the input directory, extracts archives into a cleaned directory structure, and builds the projects using CMake and Make. Build logs are stored in each project's `build` folder.

2. **Directory Cleaning:**  
   After extraction, the script flattens redundant folders, removes whitespace, and strips out the `_assignsubmission_file` substring from directory names.

3. **Build Process:**  
   It locates the folder containing `Main.cpp`, removes any existing build artifacts, creates a new `build` folder, and runs the build commands. Outputs are logged into `build.log`.

4. **Assignment Check:**  
   The check script analyzes the build logs and uses Valgrind (with its output saved to `valgrind.log`) to assess memory usage. It then compiles all results into a consolidated CSV report.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions and suggestions are welcome! Please open issues or submit pull requests for improvements or bug fixes.
