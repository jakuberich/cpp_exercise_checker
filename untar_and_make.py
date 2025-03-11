import os
import tarfile
import zipfile
import shutil
import argparse
import subprocess
from loguru import logger

def extract_archive(archive_path, target_directory):
    """
    Extracts the archive (tar.gz, .tgz, or .zip) into the target directory.
    """
    if archive_path.endswith((".tar.gz", ".tgz")):
        try:
            os.makedirs(target_directory, exist_ok=True)
            with tarfile.open(archive_path, "r:*") as tar:
                tar.extractall(path=target_directory)
            logger.info("Extracted {} into {}", archive_path, target_directory)
        except Exception as e:
            logger.error("Error extracting {}: {}", archive_path, e)
    elif archive_path.endswith(".zip"):
        try:
            os.makedirs(target_directory, exist_ok=True)
            with zipfile.ZipFile(archive_path, "r") as zip_ref:
                zip_ref.extractall(target_directory)
            logger.info("Extracted {} into {}", archive_path, target_directory)
        except Exception as e:
            logger.error("Error extracting {}: {}", archive_path, e)
    else:
        logger.warning("Unsupported file format: {}", archive_path)

def find_main_cpp_directory(directory):
    """
    Recursively searches for the directory containing 'Main.cpp' within the given directory.
    Returns the path to the directory if found, otherwise returns None.
    """
    for root, dirs, files in os.walk(directory):
        if "Main.cpp" in files:
            return root
    return None

def run_command(command, working_directory):
    """
    Runs a shell command in the specified working directory.
    Captures stdout and stderr, logs them, and returns a tuple (return_code, stdout, stderr).
    """
    logger.info("Running command '{}' in directory '{}'", command, working_directory)
    process = subprocess.Popen(
        command,
        shell=True,
        cwd=working_directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate()
    if stdout:
        logger.info("Command output:\n{}", stdout)
    if stderr:
        logger.error("Command errors:\n{}", stderr)
    return process.returncode, stdout, stderr

def build_project(project_directory):
    """
    Searches for the folder containing 'Main.cpp' within the project_directory.
    If found, deletes any existing 'build' folder, creates a new one,
    runs cmake and make in it, and saves the output of these commands to a build.log file.
    """
    main_cpp_dir = find_main_cpp_directory(project_directory)
    if main_cpp_dir is None:
        logger.warning("Main.cpp not found in project {}. Skipping build.", project_directory)
        return

    logger.info("Found Main.cpp in directory: {}", main_cpp_dir)
    build_dir = os.path.join(main_cpp_dir, "build")
    
    # Delete the existing build directory if it exists
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
            logger.info("Deleted existing build directory: {}", build_dir)
        except Exception as e:
            logger.error("Error deleting build directory {}: {}", build_dir, e)
    
    # Create a new build directory
    os.makedirs(build_dir, exist_ok=True)
    build_log_path = os.path.join(build_dir, "build.log")
    
    try:
        with open(build_log_path, "w") as log_file:
            # Run cmake
            log_file.write("=== Running cmake .. ===\n")
            ret, out, err = run_command("cmake ..", build_dir)
            log_file.write(out)
            log_file.write(err)
            if ret != 0:
                logger.error("cmake failed with return code {}", ret)
                log_file.write("cmake failed with return code {}\n".format(ret))
                return

            # Run make
            log_file.write("\n=== Running make ===\n")
            ret, out, err = run_command("make", build_dir)
            log_file.write(out)
            log_file.write(err)
            if ret != 0:
                logger.error("make failed with return code {}", ret)
                log_file.write("make failed with return code {}\n".format(ret))
            else:
                logger.info("Build completed successfully in {}", build_dir)
                log_file.write("Build completed successfully in {}\n".format(build_dir))
    except Exception as e:
        logger.exception("Error during build process in {}: {}", build_dir, e)

def main(input_dir, output_dir):
    """
    Recursively searches the input_dir for archives.
    For each archive:
    - Creates a corresponding directory in output_dir preserving the subdirectory structure,
    - Extracts the archive into a subfolder named after the archive (without extension),
    - Deletes any existing build directory in the project,
    - Searches for the folder containing 'Main.cpp' and builds the project there,
      storing the build output in a build.log file.
    """
    if not os.path.isdir(input_dir):
        logger.error("Input directory does not exist: {}", input_dir)
        return

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith((".tar.gz", ".tgz", ".zip")):
                archive_path = os.path.join(root, file)
                # Compute the relative path with respect to input_dir
                rel_path = os.path.relpath(root, input_dir)
                # Determine the project name (archive name without extension)
                if file.endswith(".tar.gz"):
                    project_name = file[:-7]  # remove ".tar.gz"
                elif file.endswith(".tgz"):
                    project_name = file[:-4]  # remove ".tgz"
                elif file.endswith(".zip"):
                    project_name = file[:-4]  # remove ".zip"
                else:
                    project_name = file

                # Create target directory preserving the subdirectory structure
                target_directory = os.path.join(output_dir, rel_path, project_name)
                os.makedirs(os.path.join(output_dir, rel_path), exist_ok=True)
                logger.info("Processing archive: {}", archive_path)
                extract_archive(archive_path, target_directory)
                build_project(target_directory)
            else:
                logger.info("Skipping unsupported file: {}", os.path.join(root, file))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Recursive extraction, cleaning build directories, and project build with logging"
    )
    parser.add_argument("input_dir", help="Path to the directory containing student archives (e.g. /path/to/archives)")
    parser.add_argument("output_dir", help="Path to the directory where extracted projects will be placed")
    args = parser.parse_args()
    main(args.input_dir, args.output_dir)
