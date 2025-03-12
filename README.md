# Recursive Extraction, Build Automation, and Assignment Check Automation

This repository contains two Python scripts designed to automate the evaluation of student C++ assignments. The first script extracts student submission archives, cleans and flattens their directory structure, and builds the projects using CMake and Make. The second script runs additional checks on the built projects by parsing build logs, executing Valgrind to detect memory issues, and (optionally) comparing the program's output with an expected output. The results are compiled into a consolidated CSV report.

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
  Searches the project's build folder for an executable file (ignoring files like `build.log` and `valgrind.log`).

- **Valgrind Memory Check:**  
  Runs Valgrind (with full leak-check enabled) on the executable and writes its output to `valgrind.log`. It then parses the output to extract the "ERROR SUMMARY" line and determines if any memory issues were found.

- **Program Output Comparison:**  
  If an expected output file is provided via the `--expected` flag, the script runs the executable normally, captures its output, and compares it with the expected output. The comparison result is recorded in the report.

- **Report Generation:**  
  Collects the following information for each project into a CSV report:
  - **Project:** Project name (derived from the directory name).
  - **Compilation_Errors:** Number of errors found in the build log.
  - **Compilation_Warnings:** Number of warnings found in the build log.
  - **Compilation_Status:** "OK" if no errors were found; otherwise "Errors".
  - **Build_Failure:** "Yes" if the build failed (due to compilation errors or a missing executable); otherwise "No".
  - **Executable:** Path to the built executable (if found).
  - **Valgrind_Status:** "OK" if no memory issues were detected, "Memory issues" if problems were found, "Valgrind Error" if a fatal error occurred, or "No executable found".
  - **Valgrind_Error_Summary:** The full "ERROR SUMMARY" line from Valgrind (or "N/A" if not available).
  - **Output_Comparison:** "Matches" if the program’s output matches the expected output, "Differs" otherwise, or "N/A" if no expected output is provided or if the build failed.

---

## Requirements

- **Python:** 3.x  
- **Packages:**
  - [loguru](https://pypi.org/project/loguru/)
  - [pandas](https://pandas.pydata.org/) (used in the check script)
- **Standard Python libraries:** `os`, `tarfile`, `zipfile`, `shutil`, `argparse`, `subprocess`
- **Build Tools:** CMake and Make must be installed.
- **Valgrind:** Must be installed on your system (ensure that necessary debug symbol packages are installed for your system).

---

## Installation

1. **Clone or download the repository.**

2. **Install Python dependencies:**

   ```bash
   pip install loguru pandas
   ```
   
   Or, if using conda:
   
   ```bash
   conda install -c conda-forge loguru pandas
   ```

3. **Ensure that CMake, Make, and Valgrind are installed on your system.**

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

After all projects have been built, run the second script to perform additional checks and generate a CSV report:

```bash
python3 check_assignments.py /path/to/output --report report.csv --expected expected_output.txt
```

- **`/path/to/output`** is the root directory where your built projects are located (i.e. the output from the extraction/build script).
- **`--report report.csv`** (optional) specifies the name of the CSV report file. If not provided, the default is `report.csv`.
- **`--expected expected_output.txt`** (optional) specifies the path to a text file containing the expected output of the program. If provided, the script compares each executable's output with this expected output.

The generated CSV report will include detailed information about each project.

---

## How It Works

1. **Extraction:**  
   The extraction script scans the input directory, extracts archives into a cleaned and flattened directory structure, and builds the projects using CMake and Make. Build logs are stored in each project's `build` folder.

2. **Directory Cleaning:**  
   After extraction, the script flattens redundant folders, removes whitespace, and strips out the `_assignsubmission_file` substring from directory names.

3. **Build Process:**  
   The script locates the folder containing `Main.cpp`, removes any existing build artifacts, creates a new `build` folder, and runs the build commands. Output is logged to `build.log`.

4. **Assignment Check:**  
   The check script analyzes build logs for errors/warnings, detects the built executable, and runs Valgrind (saving its output to `valgrind.log`) to assess memory usage. If an expected output is provided, the script runs the program normally and compares its output to the expected result. All results are compiled into a CSV report.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Contributing

Contributions and suggestions for improvements are welcome! Please open issues or submit pull requests for bug fixes or additional features.