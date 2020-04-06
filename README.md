# CSV Fuzzy Duplicate Remover
A simple utility to remove duplicate (or near-duplicate) entries from a CSV file, according to user-specified match criteria.

Takes an input CSV file and checks whether each row already exists in the file, outputting each unique row only once. 

A row is identified as a duplicate if its values in a user-specified subset of columns match those of any other row. The meaning of "matching" is determined according to a choice of comparison methods. 

When more than one column is specified, a duplicate row is only identified when there is some other row in the datafile which matches all of those columns (according to their specified match methods).

## Usage
```
python remove_duplicates.py <datafile_path> <specfile_path> <output_directory_path>
```

`<datafile_path>` is the path to a CSV datafile.
`<specfile_path>` is the path to a JSON specfile describing how to identify duplicate rows in the datafile.      
`<output_directory_path>` is the path to the directory in which the output CSV file should be saved.

## Specification Files
The columns within which to check for matches and the methods for identifying matches within each column are defined in a specification `.json` file.

In the following example, values in the column called "Title" are matched according to the `exact_lower_alphanumeric` method, and values in the column called "Year" are matched according to the `exact` method.

```json
{
    "Title": {
        "method": "exact_lower_alphanumeric"
    },
    "Year": {
        "method": "exact"
    }
}
```

## Matching Methods

Considering the following example strings, the available matching methods for specification files work as follows:
```python
a = "The Quick Brown Fox..."
b = "the quick brown fox..."
c = "theqUi $ck brOwn?foX"
d = "the quicker brown fox"
```

Method | Match Description | Example Matches
--- | --- | ---
`exact` | Only identical string values. | `a=a`, `b=b`, `c=c` 
`exact_case_insensitive` | Any strings with the same characters in the same positions, regardless of alphabetic character case. | **`a=b`**, `a=a`, `b=b`, `c=c`
`exact_lower_alphanumeric` | Any strings in which the sequence of numeric and lower-case alphabetic characters is identical | **`a=c`**, **`b=c`**, `a=b`, `a=a`, `b=b`, `c=c`