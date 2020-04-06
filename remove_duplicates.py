import csv
import json
import sys
import pandas as pd
import re
from typing import Dict, List, Callable
from pathlib import Path

ATTRIBUTE_METHOD = "method"

METHOD_EXACT = "exact"
METHOD_EXACT_CASE_INSENSITIVE = "exact_case_insensitive"
METHOD_EXACT_LOWERCASE_ALPHANUMERIC = "exact_lower_alphanumeric"

OUTPUT_FILE_SUFFIX = "_duplicates_removed.csv"


# Command line usage help message
USAGE_MESSAGE = "\nUsage:\n"\
                "    python {0} <datafile_path> <specfile_path> <output_directory_path>\n\n"\
                "<datafile_path> is the path to a CSV datafile.\n"\
                "<specfile_path> is the path to a JSON specfile describing how to identify duplicate rows in the datafile.\n"\
                "<output_directory_path> is the path to the directory in which the output CSV file should be saved.\n"


def remove_duplicates(source: Path, criteria: Dict[str, Dict[str, str]]):
    """
    Load a ".csv" file and remove its duplicate entires, according to the given criteria.
    """
    tracked_rows = {}
    row_count = 0
    with open(source) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_count += 1
            vhfs = [get_value_hash_function(
                criteria[column_key]) for column_key in criteria]
            tracked_rows = track_row(row, criteria.keys(), vhfs, tracked_rows)
    print(
        f"Removed {row_count - len(tracked_rows)} duplicate(s) from {row_count} row(s).")
    return tracked_rows.values()


def get_value_hash_function(method_and_params: Dict[str, str]):
    """
    Map a method name from the spec to a specific string processing function.
    
    These functions are used in a similar way to hash functions, but, for each,
    similar input strings should be mapped to identical outputs (which is not what 
    typical hash functions are designed to do). In essence, these functions define
    what it means for two strings to be "similar".
    """
    if ATTRIBUTE_METHOD in method_and_params:
        method = method_and_params[ATTRIBUTE_METHOD]
        if method == METHOD_EXACT:
            return lambda x: x
        elif method == METHOD_EXACT_CASE_INSENSITIVE:
            return lambda x: x.lower()
        elif method == METHOD_EXACT_LOWERCASE_ALPHANUMERIC:
            return lambda x: re.sub("[^a-z0-9]+", "", x.lower())
        else:
            raise ValueError(
                f"The value hash method '{method}' was not recognised")
    raise KeyError(
        f"The given method dictionary contains no '{ATTRIBUTE_METHOD}' key.")


def track_row(row: Dict, column_keys: List[str], value_hash_functions: List[Callable[[str], str]], unique_rows: Dict) -> Dict:
    """
    Add a row to the given dict if it is not already in that dict, using the specified columns and their 
    (processed) values are used as a unique identifier to check if the row is already present.

    Implementation details:
    Take a dict representing a row from a ".csv" file, map the values in selected columns to a unique hash value,
    then add the original row as a value in the "unique_rows" dict, indexed using the unique hash value as its key.
    """
    hashed_key = ""
    for i, column_key in enumerate(column_keys):
        if column_key in row:
            hashed_key += value_hash_functions[i](row[column_key])
        else:
            raise KeyError(
                f"The given column key ('{column_key}') does not exist in the current row of data.")

    unique_rows[hashed_key] = row
    return unique_rows


def main(datafile: Path, specfile: Path, outputdirectory: Path):
    """
    Remove the duplicates from the given file according to the given specification,
    saving the results in a ".csv" file in the given directory.
    """
    specification_dict = {}
    with open(specfile) as spec:
        specification_dict = json.load(spec)
    results = remove_duplicates(datafile, specification_dict)
    df = pd.DataFrame(results)
    df.to_csv(Path(outputdirectory, datafile.stem +
                   OUTPUT_FILE_SUFFIX), index=False)


if __name__ == "__main__":
    arg_count = len(sys.argv[1:])
    data_path = ""
    spec_path = ""
    output_path = ""
    if arg_count == 3:
        data_path = Path(sys.argv[1])
        spec_path = Path(sys.argv[2])
        output_path = Path(sys.argv[3])
    else:
        print(
            f"Incorrect number of arguments given ({arg_count}). Expected 3.")
        raise SystemExit(USAGE_MESSAGE.format(sys.argv[0]))

    invalid = False
    if not data_path.is_file():
        print(
            f"The given datafile path ('{data_path}') does not refer to a file.")
        invalid = True
    if not spec_path.is_file():
        print(
            f"The given specification file path ('{spec_path}') does not refer to a file.")
        invalid = True
    if not output_path.is_dir():
        print(
            f"The given output file path ('{output_path}') does not refer to a directory.")
        invalid = True
    if invalid:
        raise SystemExit(USAGE_MESSAGE.format(sys.argv[0]))
    else:
        main(data_path, spec_path, output_path)
