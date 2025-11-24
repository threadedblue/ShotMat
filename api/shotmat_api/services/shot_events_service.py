import D4M.assoc as d4m_assoc
from typing import List, Dict, Any, Optional

def load_tsv_to_assoc(file_path: str) -> Optional[d4m_assoc.Assoc]:
    """
    Loads data from a TSV file into a D4M associative array (Assoc).
    The TSV is expected to be in a triple format (row, column, value).
    It skips the header row.

    Args:
        file_path: The path to the TSV file.

    Returns:
        A d4m_assoc.Assoc object containing the data, or None if file not found.
    """
    try:
        # readcsv with triples=True reads 3-column data into an Assoc array.
        # skip=1 tells it to ignore the header row.
        assoc_array = d4m_assoc.readcsv(file_path, triples=True, delimiter='\t', skip=1)
        return assoc_array
    except FileNotFoundError:
        print(f"Warning: File not found at {file_path}")
        return None

def load_matrix_tsv_to_assoc(file_path: str) -> Optional[d4m_assoc.Assoc]:
    """
    Loads data from a TSV file into a D4M associative array (Assoc).
    The TSV is expected to be in a matrix format with headers.

    Args:
        file_path: The path to the TSV file.

    Returns:
        A d4m_assoc.Assoc object containing the data, or None if file not found.
    """
    try:
        # readcsv with labels=True reads matrix-style data with headers.
        assoc_array = d4m_assoc.readcsv(file_path, labels=True, delimiter='\t')
        return assoc_array
    except FileNotFoundError:
        print(f"Warning: File not found at {file_path}")
        return None

def save_assoc_to_tsv(file_path: str, assoc_array: d4m_assoc.Assoc, headers: List[str]):
    """
    Saves a D4M associative array (Assoc) to a TSV file.

    Args:
        file_path: The path to the TSV file to save.
        assoc_array: The Assoc object to write.
        headers: A list of strings for the header columns (e.g., ["row_id", "col_id", "value"]).
    """
    # writecsv will write the Assoc object out in triple format.
    d4m_assoc.writecsv(assoc_array, file_path, delimiter='\t', write_headers=True, 
                       row_label=headers[0], col_label=headers[1], val_label=headers[2])

def assoc_to_json_structure(assoc_array: d4m_assoc.Assoc) -> Dict[str, Any]:
    """
    Converts a D4M associative array (Assoc) into a specific JSON structure.

    The function reconstructs table rows from the (row, column, value) triples
    stored in the associative array.

    Args:
        assoc_array: The Assoc object to convert.

    Returns:
        A dictionary matching the desired JSON structure.
    """
    if not assoc_array:
        return {"cols": [], "rows": []}

    # Get all the triples from the associative array.
    row_keys, col_keys, vals = assoc_array.find()

    # Determine the columns for the output JSON.
    # It includes 'row_id' plus all unique column keys found in the data.
    json_cols = ["row_id"] + sorted(list(set(col_keys)))

    # Reconstruct the rows.
    # We group the triples by their row_key.
    reconstructed_rows: Dict[str, Dict[str, Any]] = {}
    for r, c, v in zip(row_keys, col_keys, vals):
        if r not in reconstructed_rows:
            # Initialize the row with default null values for all possible columns.
            reconstructed_rows[r] = {col_name: None for col_name in json_cols}
            reconstructed_rows[r]["row_id"] = r
        
        # Set the specific value for the column in this row.
        reconstructed_rows[r][c] = v

    # Convert the dictionary of rows into a list for the final JSON structure.
    json_rows = list(reconstructed_rows.values())

    return {"cols": json_cols, "rows": json_rows}