import re
import json
from pathlib import Path
import os
from argparse import ArgumentParser


def process_file(args, change_list, to_process):
    original = open(to_process, 'r')

    if args.Make | args.Replace:
        suffix = Path(to_process).suffix
        to_write = to_process.replace(suffix, (' -Changed' + suffix))
        changed_file = open(to_write, 'w')

        # Run it as many times as needed
        for line in original.readlines():
            changed_file.write(make_changes(args, change_list, line))

        # Tie up the streams and replace the original file
        changed_file.close()
        if args.Replace:
            os.remove(to_process)
            os.rename(to_write, to_process)

    else:
        for line in original.readlines():
            print(make_changes(args, change_list, line))

    original.close()
    return 0


def make_changes(args, change_list, line):
    changed = line
    if args.LowerCase:
        changed = line.lower()

    for c in change_list.keys():
        pattern = re.compile(c)
        changed = re.sub(pattern, change_list.get(c), changed)

    return changed


def recursive_process(path, to_scan):
    for path in os.listdir(path):
        if Path(path).suffix in to_scan:
            process_file(path)
        elif Path.is_dir(path):
            recursive_process(path)
    return 0


def process_dir(dir, to_scan):
    for path in os.listdir(dir):
        if Path(path).suffix in to_scan:
            process_file(path)


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
        # print("Error in trying to read: ", dictionary)


def setup_parser():
    """
    process the input.
            Command list:
                -e = make an example dictionary
                -f = File to be searched, to be followed by a File/path.txt
                -s = String to processed, to be followed by "String for processing."
                -d = read in a dictionary, to be followed by a dictionary/path.json.
                -r = Replace, replace the original file.
                -m = make a new file.
                -b = Backward, reverse the replacement and target of the inputs
                -c = Change to be made, to be followed by "target:replacement"
                -l = set the text to lower case before applying changes.
                Set the path to start the recursive process in. Defaults to current working directory.
                -a = All files, repeat replacement for all files in cwd
                -s = All subdirectories, repeat for all files in subdirectories

    """
    parser = ArgumentParser(description='Find matches of a pattern in ' \
                                        'lines of file(s).', add_help=False)
    parser.add_argument('--help', action='help', help='show this help ' \
                                                      'message and exit')
    parser.add_argument('-e', '--Example', action='store_true',
                        help='Creates am example change dictionary in cwd.')
    parser.add_argument('-f', '--File', action='append',
                        help='File(s) to be processed.')
    parser.add_argument('-s', '--String', action='append',
                        help='String(s) to be processed and printed to terminal.')
    parser.add_argument('-d', '--Dictionary', action='append',
                        help='Dictionary of target:replacement pairs to be applied.')
    parser.add_argument('-r', '--Replace', action='store_true',
                        help='Delete and replace the original files, otherwise create changed copies.')
    parser.add_argument('-m', '--Make', action='store_true',
                        help='Make a new file containing the result.')
    parser.add_argument('-b', '--Backwards', action='store_true',
                        help='Reverse all of the target:replacements pairs in the process.')
    parser.add_argument('-c', '--Change', action='append',
                        help='A change to be applied, entered as: "target:replacement"')
    parser.add_argument('-l', '--LowerCase', action='store_true',
                        help='Set all text to lower case before applying changes.')
    parser.add_argument('-z', '--Recursive', action='append',
                        help='Input a specific path to start a recursive process in. Default = .txt only.')
    parser.add_argument('-a', '--All', action='append',
                        help='Input a specific directory to process all files in. Default = .txt only')
    parser.add_argument('-t', '--Type', action='append',
                        help='Add a file type to scan when processing directories with -a or -r.')
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
        # print("Error in creating example dictionary.")


def main() -> int:
    parser = setup_parser()

    args = parser.parse_args()
    change_list = dict()
    to_scan = ['.txt']

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

    # # Starting Report
    # if len(change_list) > 0:
    #     print("Set to perform these changes: \n")
    #     for c in change_list.items():
    #         print(c)
    # if args.Replace:
    #     print("Original files will be replaced.\n")
    # else:
    #     print("New files will be created.\n")

    # Begin Processing
    if args.Type is not None:
        to_scan += args.Type

    if args.All is not None:
        for path in args.All:
            process_dir(args.All, to_scan)

    if args.Recursive is not None:
        for path in args.Recursive:
            recursive_process(path, to_scan)

    if args.String is not None:
        for s in args.String:
            changed = make_changes(args, change_list, s)
            print(s + " -> \n" + changed + "\n")

    if args.File is not None:
        for f in args.File:
            process_file(args, change_list, f)

    return 0


if __name__ == '__main__':
    main()
