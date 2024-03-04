import re
import json
from pathlib import Path
import os
from argparse import ArgumentParser


def individual_process(change_list, to_search, replace_original):
    print("Processing ", to_search)
    original = open(to_search, 'r')

    suffix = Path(to_search).suffix
    to_write = to_search.replace(suffix, (' -Changed' + suffix))
    changed_file = open(to_write, 'w')

    # Run it as many times as needed
    for line in original.readlines():
        for c in change_list.keys():
            pattern = re.compile(c)
            line = re.sub(pattern, change_list[c], line)
        changed_file.write(line)

    # Tie up the streams and replace the original file
    original.close()
    changed_file.close()
    if replace_original:
        os.remove(to_search)
        os.rename(to_write, to_search)

    return 0


def recursive_process(dir, types, changes, replace_original):
    for path in os.listdir(dir):
        print("Working through Directory: ", path, '\n')
        if Path(path).suffix in types:
            individual_process(path, changes, replace_original)
        elif Path.is_dir(path):
            recursive_process(path, types, changes, replace_original)

    return 0


def add_dictionary(changes, dictionary):
    """Read in and decode a json dictionary."""
    try:
        if Path(dictionary).suffix == '.json':

            dfile = open(dictionary, 'r')
            d = json.load(dfile)

            keys = list(d.keys())
            values = list(d.values())

            i = 0
            while i < len(d):
                changes[keys[i]] = values[i]
                i += 1
            dfile.close()
    except OSError as e:
        print("Error in trying to read: ", e)
        #print("Error in trying to read: ", dictionary)


def setup_parser():
    """
    process the input.
            Command list:
                -e = make an example dictionary
                -f = File to be searched to be followed by a File/path.txt
                -d = read in a dictionary, to be followed by a dictionary/path.json.
                -b = Backward, reverse the replacement and target of the inputs
                -r = Replace, replace the original file instead of making a new one.
                -a = All files, repeat replacement for all files in cwd
                -s = All subdirectories, repeat for all files in subdirectories
                -c = Change to be made, to be followed by "target:replacement"
    """
    parser = ArgumentParser(description='Find matches of a pattern in ' \
                                        'lines of file(s).', add_help=False)
    parser.add_argument('--help', action='help', help='show this help ' \
                                                      'message and exit')

    parser.add_argument('-e', '--Example', action='store_true',
                        help='Creates am example change dictionary in cwd.')
    parser.add_argument('-f', '--File', action='append',
                        help='File(s) to be processed.')
    parser.add_argument('-d', '--Dictionary', action='append',
                        help='Dictionary of target:replacement pairs to be applied.')
    parser.add_argument('-r', '--Replace', action='store_true',
                        help='Delete and replace the original files, otherwise create changed copies.')
    parser.add_argument('-b', '--Backwards', action='store_true',
                        help='Reverse all of the target:replacements pairs in the process.')
    parser.add_argument('-c', '--Change', action='append',
                        help='A "target:replacement" change to be applied.')
    parser.add_argument('-a', '--All', action='store_true',
                        help='Recursively process all files in all subdirectories in cwd.')
    parser.add_argument('-t', '--Type', action='append',
                        help='Add a file type to scan when processing all files.')
    # parser.add_argument('-p', '--Path', action='store_ture',
    #                     help='Input a specific directory to start a recursive process in.')
    # parser.add_argument('-i', '--ignore-case', action='store_true',
    #                     help='case-insensitive search')

    return parser


def make_example_dictionary():
    """Creates an example json dictionary file inside the current working directory."""

    example = "exampleDict.json"
    try:
        file = open(example, 'w')
        file.write('{\n')
        file.write('    \"target1\":\"replacement1\",\n')
        file.write('    \"target2\":\"replacement2\"\n')
        file.write('}')
        file.close()
        print("Example Dictionary made at: ", os.getcwd(), example)
    except OSError as e:
        print("Error in creating example dictionary: ", e)
        #print("Error in creating example dictionary.")


def main() -> int:
    parser = setup_parser()
    args = parser.parse_args()

    change_list = dict()
    if args.Change is not None:
        for c in args.Change:
            pair = c.split(':')
            change_list[pair[0]] = pair[1]

    if args.Dictionary is not None:
        for dictionary in args.Dictionary:
            add_dictionary(change_list, dictionary)

    if args.Example is True:
        make_example_dictionary()

    if args.Backwards is True:
        reverse_list = dict()
        keys = list(change_list.keys())
        values = list(change_list.values())
        i = 0
        while i < change_list.__len__():
            reverse_list[values[i]] = keys[i]
            i += 1
        change_list = reverse_list

    # Starting Report
    if len(change_list) > 0:
        print("Set to perform these changes: \n")
        for c in change_list.items():
            print(c)
    if args.Replace:
        print("Original files will be replaced.\n")
    else:
        print("New files will be created.\n")


    # Begin Processing
    if args.All is True:
        print("Beginning Recursive Process.\n")
        to_scan = ['.txt']
        if args.Type is not None:
            to_scan += args.Type
        recursive_process(os.getcwd(), to_scan, change_list, args.Replace)
    elif args.File is not None:
        for f in args.File:
            individual_process(change_list, f, args.Replace)

    return 0


if __name__ == '__main__':
    main()
