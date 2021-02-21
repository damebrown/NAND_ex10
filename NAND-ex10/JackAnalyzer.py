import os.path
import sys
import file_parser as fp
import CompilationEngine as ce


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('No folder was specified. please enter a file or folder'
              'name in system args.')
    else:
        for i in range(1, len(sys.argv)):
            file_list = fp.directory_parser(sys.argv[i])
            dir_name = fp.get_dir_name(sys.argv[i])
            for path in file_list:
                try:
                    lines = fp.file_reader(path)
                    name = fp.name_extractor(path)
                    engine = ce.CompilationEngine(lines)
                    xml_path = file_list[0]
                    if os.path.isdir(sys.argv[i]):
                        name += '.xml'
                        dir_path = os.path.abspath(sys.argv[i])
                        xml_path = os.path.sep.join([dir_path, name])
                    fp.file_writer(engine.compile(), xml_path)
                except SyntaxError as e:
                    print("Error translating file:\n{0}"
                          "\nwith error:\n{1}".format(path, e))
                except IOError as e:
                    print("Error parsing file:\n{0}\nwith error:\n{1}".format(path, e.strerror))
