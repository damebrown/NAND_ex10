import os
import re


def directory_parser(path):
    """
    parses the input the program has got into an array of absolute paths of
    files to work with
    :param path: the input path
    :return: a list of absolute paths of files to work with
    """
    if os.path.isdir(path):
        path_array, valid_paths = os.listdir(path), []
        for index, dir_path in enumerate(path_array):
            dir_path = os.path.abspath(os.path.sep.join([path, dir_path]))
            if dir_path.endswith(".jack") and not os.path.isdir(path_array[index]):
                valid_paths.append(dir_path)
        return valid_paths
    else:
        return [os.path.abspath(os.path.sep.join([path]))]


def clean_empty(lines_array):
    """
    cleans empty lines from the .jack files
    :param lines_array: the array of lines to clean
    :return: the clean array
    """
    for line in lines_array:
        if line == '':
            lines_array.remove(line)
    return lines_array


def file_reader(jack_path):
    """
    reads a file, returns a list of the file's lines
    :param jack_path: the path of the .jack file to read
    :return: the array of the file's line, minus empty lines
    """
    with open(jack_path) as file:
        lines_array = file.readlines()
    lines_array = [line.strip('\n') for line in lines_array]
    return clean_empty(lines_array)


def file_writer(command_array, jack_path):
    """
    writes the array of binary commands to a new .hack file with the same name
    :param command_array: the array of binary commands
    :param jack_path: the path of the .jack file's .hack aquivilant to write to
    """
    new_name = jack_path.replace('.jack', '.xml')
    with open(new_name, "w") as file:
        for command in command_array:
            file.write(command)
            file.write('\n')


def name_extractor(path):
    """
    returns a .jack file's name
    :param path: the file's path
    :return: the file's name
    """
    file_name = os.path.basename(path)
    return file_name.strip('.jack')


def get_dir_name(path):
    """
    returns a directory's name
    :param path: the directory's path
    :return: the directory's name
    """
    return os.path.basename(os.path.normpath(path))
