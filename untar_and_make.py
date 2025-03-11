import os
import tarfile
import zipfile
import shutil
import argparse
import subprocess
from loguru import logger

def simplify_extracted_directory(target_directory):
    """
    Simplify the extracted directory structure by flattening out unnecessary single-directory wrappers.
    If target_directory contains exactly one subdirectory and no files, move that subdirectory's contents up 
    and remove the redundant folder. Repeat until no single subdirectory remains.
    """
    while True:
        items = os.listdir(target_directory)
        if len(items) == 1:
            single_item = os.path.join(target_directory, items[0])
            if os.path.isdir(single_item):
                for sub_item in os.listdir(single_item):
                    src = os.path.join(single_item, sub_item)
                    dst = os.path.join(target_directory, sub_item)
                    shutil.move(src, dst)
                os.rmdir(single_item)
                logger.info("Simplified directory structure by removing redundant folder: {}", single_item)
                continue
        break

def remove_whitespace_from_paths(directory):
    """
    Recursively renames all files and directories in the given directory by removing whitespace characters from their names.
    """
    for root, dirs, files in os.walk(directory, topdown=False):
        for file in files:
            new_file = file.replace(" ", "_")
            if new_file != file:
                old_path = os.path.join(root, file)
                new_path = os.path.join(root, new_file)
                os.rename(old_path, new_path)
                logger.info("Renamed file {} to {}", old_path, new_path)
        for d in dirs:
            new_d = d.replace(" ", "_")
            if new_d != d:
                old_path = os.path.join(root, d)
                new_path = os.path.join(root, new_d)
                os.rename(old_path, new_path)
                logger.info("Renamed directory {} to {}", old_path, new_path)

def remove_assignsubmission_folder(directory):
    """
    Checks for any subdirectory whose name contains '_assignsubmission_file'.
    If found, moves its contents up to the given directory and removes the folder.
    """
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and "_assignsubmission_file" in item:
            for sub_item in os.listdir(item_path):
                src = os.path.join(item_path, sub_item)
                dst = os.path.join(directory, sub_item)
                shutil.move(src, dst)
            os.rmdir(item_path)
            logger.info("Removed assignsubmission folder: {}", item_path)

def filter_specific_warning(text):
    """
    Filters out the specific CMake deprecation warning regarding compatibility with CMake < 3.5.
    Only removes the block of text associated with that warning, leaving other warnings intact.
    """
    lines = text.splitlines(keepends=True)
    filtered_lines = []
    skip = False
    for line in lines:
        if not skip and "CMake Deprecation Warning" in line and "cmake_minimum_required" in line:
            skip = True
            continue
        if skip:
            if line.startswith("  ") or line.strip() == "":
                continue
            else:
                skip = False
        filtered_lines.append(line)
    return "".join(filtered_lines)

def run_command(command, working_directory):
    """
    Runs a shell command in the specified working directory.
    Captures stdout and stderr, filters out the specific CMake deprecation warning for cmake commands,
    logs the results, and returns a tuple (return_code, stdout, stderr).
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
    
    # If this is a cmake command, filter out only the specific deprecation warning.
    if "cmake" in command:
        stdout = filter_specific_warning(stdout)
        stderr = filter_specific_warning(stderr)
    
    if stdout:
        logger.info("Command output:\n{}", stdout)
    if stderr:
        logger.error("Command errors:\n{}", stderr)
    return process.returncode, stdout, stderr

def extract_archive(archive_path, target_directory):
    """
    Extracts the archive (tar.gz, .tgz, or .zip) into the target directory.
    Then simplifies the directory structure, removes whitespace characters from paths, and
    removes any extra '_assignsubmission_file' folder layer.
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
    
    simplify_extracted_directory(target_directory)
    remove_whitespace_from_paths(target_directory)
    remove_assignsubmission_folder(target_directory)

def find_main_cpp_directory(directory):
    """
    Recursively searches for the directory containing 'Main.cpp' within the given directory.
    Returns the path to that directory if found, otherwise returns None.
    """
    for root, dirs, files in os.walk(directory):
        if "Main.cpp" in files:
            return root
    return None

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
    
    if os.path.exists(build_dir):
        try:
            shutil.rmtree(build_dir)
            logger.info("Deleted existing build directory: {}", build_dir)
        except Exception as e:
            logger.error("Error deleting build directory {}: {}", build_dir, e)
    
    os.makedirs(build_dir, exist_ok=True)
    build_log_path = os.path.join(build_dir, "build.log")
    
    try:
        with open(build_log_path, "w") as log_file:
            log_file.write("=== Running cmake .. ===\n")
            cmake_command = "cmake .."
            ret, out, err = run_command(cmake_command, build_dir)
            log_file.write(out)
            log_file.write(err)
            if ret != 0:
                logger.error("cmake failed with return code {}", ret)
                log_file.write("cmake failed with return code {}\n".format(ret))
                return

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
    - When the student's folder (from the relative path) contains '_assignsubmission_file',
      it is removed from the final folder name.
    - If such a folder is detected, the archive's own subfolder is omitted to avoid extra nesting.
    - Extracts the archive into the target directory, simplifies its path, and builds the project.
    """
    if not os.path.isdir(input_dir):
        logger.error("Input directory does not exist: {}", input_dir)
        return

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith((".tar.gz", ".tgz", ".zip")):
                archive_path = os.path.join(root, file)
                # Compute the relative path with respect to input_dir.
                rel_path = os.path.relpath(root, input_dir)
                # Clean the relative path: remove whitespaces and remove the substring "_assignsubmission_file"
                clean_rel_path = os.path.sep.join(part.replace(" ", "_") for part in rel_path.split(os.path.sep))
                if "_assignsubmission_file" in clean_rel_path:
                    clean_rel_path = clean_rel_path.replace("_assignsubmission_file", "")
                    # When the student's folder already has the assignsubmission substring, do not add an extra project folder.
                    target_directory = os.path.join(output_dir, clean_rel_path)
                else:
                    # Determine the project name (archive name without extension), also remove spaces.
                    if file.endswith(".tar.gz"):
                        project_name = file[:-7]
                    elif file.endswith(".tgz"):
                        project_name = file[:-4]
                    elif file.endswith(".zip"):
                        project_name = file[:-4]
                    else:
                        project_name = file
                    project_name = project_name.replace(" ", "_")
                    target_directory = os.path.join(output_dir, clean_rel_path, project_name)

                # Ensure the directory for the clean relative path exists.
                os.makedirs(os.path.join(output_dir, clean_rel_path), exist_ok=True)
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
