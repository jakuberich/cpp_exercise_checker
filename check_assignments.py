import os
import re
import subprocess
import pandas as pd
from loguru import logger

def parse_build_log(build_log_path):
    """
    Parse build.log to extract compilation errors and warnings.
    Returns a tuple: (error_count, warning_count).
    Uses a simple heuristic that counts lines containing "error" or "warning".
    """
    errors = 0
    warnings = 0
    if not os.path.exists(build_log_path):
        return errors, warnings
    with open(build_log_path, 'r') as f:
        for line in f:
            if re.search(r'error', line, re.IGNORECASE):
                errors += 1
            if re.search(r'warning', line, re.IGNORECASE):
                warnings += 1
    return errors, warnings

def find_executable(build_dir):
    """
    Searches the build directory for an executable file.
    Returns the first file that is executable (ignoring build.log and valgrind.log).
    """
    for root, dirs, files in os.walk(build_dir):
        for file in files:
            if file in ["build.log", "valgrind.log"]:
                continue
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                return file_path
    return None

def run_valgrind(executable_path, build_dir):
    """
    Runs valgrind on the executable with full leak check.
    Writes the output to 'valgrind.log' in the build directory.
    Returns a tuple: (exit_code, output).
    """
    log_path = os.path.join(build_dir, "valgrind.log")
    cmd = f"valgrind --leak-check=full {executable_path}"
    try:
        result = subprocess.run(
            cmd, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout + "\n" + result.stderr
        with open(log_path, "w") as f:
            f.write(output)
        logger.info("Valgrind output written to {}", log_path)
        return result.returncode, output
    except Exception as e:
        logger.error("Error running valgrind on {}: {}", executable_path, e)
        return -1, ""

def parse_valgrind_log(valgrind_output):
    """
    Parses the Valgrind output to determine if memory issues were found.
    Also extracts the "ERROR SUMMARY" line.
    Returns a tuple (memory_status, error_summary) where:
    - memory_status: "OK" if no errors are found, "Memory issues" if errors > 0,
      "Valgrind Error" if a fatal error is detected, or "Unknown".
    - error_summary: the full ERROR SUMMARY line if found, otherwise "N/A".
    """
    if "Fatal error at startup" in valgrind_output:
        return "Valgrind Error", "Fatal error at startup"
    match = re.search(r"(ERROR SUMMARY:\s+\d+\s+errors.*)", valgrind_output)
    if match:
        error_summary = match.group(1).strip()
        error_count_match = re.search(r"ERROR SUMMARY:\s+(\d+)\s+errors", error_summary)
        if error_count_match:
            error_count = int(error_count_match.group(1))
            memory_status = "OK" if error_count == 0 else "Memory issues"
            return memory_status, error_summary
    return "Unknown", "N/A"

def main(output_dir, report_csv="report.csv"):
    """
    Traverse the output directory (produced by the build script) to find each built project.
    For each project (assumed to be a subdirectory containing a 'build' folder):
      - Parse build.log for compilation errors and warnings.
      - Mark the build as failed if there are any compilation errors or no executable is found.
      - If the build succeeded, run Valgrind on the executable and parse its output from 'valgrind.log'
        to determine memory issues and extract the error summary.
    Collected data is stored in a CSV report.
    """
    data = []
    for root, dirs, files in os.walk(output_dir):
        if "build" in dirs:
            project_dir = root
            build_dir = os.path.join(project_dir, "build")
            build_log_path = os.path.join(build_dir, "build.log")
            comp_errors, comp_warnings = parse_build_log(build_log_path)
            compilation_status = "OK" if comp_errors == 0 else "Errors"
            build_failure = "No"
            if comp_errors > 0:
                build_failure = "Yes"
            exe_path = find_executable(build_dir)
            if not exe_path:
                build_failure = "Yes"
                memory_status = "No executable found"
                valgrind_summary = "N/A"
            else:
                if build_failure == "Yes":
                    memory_status = "N/A"
                    valgrind_summary = "N/A"
                else:
                    ret, valgrind_output = run_valgrind(exe_path, build_dir)
                    memory_status, valgrind_summary = parse_valgrind_log(valgrind_output)
            project_name = os.path.basename(project_dir)
            data.append({
                "Project": project_name,
                "Compilation_Errors": comp_errors,
                "Compilation_Warnings": comp_warnings,
                "Compilation_Status": compilation_status,
                "Build_Failure": build_failure,
                "Executable": exe_path if exe_path else "",
                "Valgrind_Status": memory_status,
                "Valgrind_Error_Summary": valgrind_summary
            })
    df = pd.DataFrame(data)
    df.to_csv(report_csv, index=False)
    print("Report generated:", report_csv)
    print(df)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Check built projects for compilation issues and memory leaks using Valgrind."
    )
    parser.add_argument("output_dir", help="Path to the directory containing built projects (output from the extraction/build script).")
    parser.add_argument("--report", default="report.csv", help="Output CSV report file (default: report.csv).")
    args = parser.parse_args()
    main(args.output_dir, args.report)
