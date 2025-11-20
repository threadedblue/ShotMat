import sys
print("PYTHON FROM SCRIPT:", sys.executable)
import D4M
print("D4M FROM SCRIPT:", D4M.__file__)


import D4M.assoc as d4m_assoc
from typing import List, Dict, Any
import os

def load_tsv(file_path: str) -> List[Dict[str, Any]]:
    """
    Loads data from a TSV file into a list of dictionaries.

    Args:
        file_path: The path to the TSV file.

    Returns:
        A list of dictionaries, where each dictionary represents a row.
    """
    # d4m.assoc.readcsv with triples=True expects no header. We skip it.
    with open(file_path, 'r', encoding='utf-8') as f:
        headers = f.readline().strip().split('\t')
        # Create a temporary file without the header/Users/gcr/ShotMat.Wk/shotmat/api/.venv/bin/python /Users/gcr/ShotMat.Wk/shotmat/data_store/d4m_data_io.py

        temp_file_path = file_path + ".tmp"
        with open(temp_file_path, 'w', encoding='utf-8') as tmp_f:
            tmp_f.write(f.read())

    assoc_array = d4m_assoc.readcsv(temp_file_path, triples=True, delimiter='\t', labels=False)
    os.remove(temp_file_path)

    rows, cols, vals = assoc_array.find()
    return [{headers[0]: r, headers[1]: c, headers[2]: v} for r, c, v in zip(rows, cols, vals)]

def save_tsv(file_path: str, data: List[Dict[str, Any]], headers: List[str]):
    """
    Saves a list of dictionaries to a TSV file.

    Args:
        file_path: The path to the TSV file to save.
        data: A list of dictionaries to write.
        headers: A list of strings representing the header columns.
    """
    if not data:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\t'.join(headers) + '\n')
        return

    assoc_array = d4m_assoc.Assoc(data[0].keys(), data[1].keys(), data[2].keys())
    d4m_assoc.writecsv(assoc_array, file_path, delimiter='\t')
