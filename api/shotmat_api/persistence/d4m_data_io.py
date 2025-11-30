import D4M.assoc as d4m_assoc
from typing import Any, Dict, List


def writejson(assoc: d4m_assoc.Assoc) -> Dict[str, Any]:
    """
    Serialize a D4M Assoc into a JSON-serializable dict with the structure:
    {
      "rows": [...],
      "cols": [...],
      "entries": [
        {"row": ..., "col": ..., "val": ...},
        ...
      ]
    }

    This must be a lossless representation: reconstructing via readjson()
    must yield an AA equivalent to the original.

    Args:
        assoc: The D4M Assoc object to serialize.

    Returns:
        A dictionary in the canonical AA JSON format.
    """
    row_keys, col_keys, vals = assoc.find()

    # Get unique row and column labels, sorted for stable output
    unique_rows = sorted(list(set(row_keys)))
    unique_cols = sorted(list(set(col_keys)))

    entries = [
        {"row": r, "col": c, "val": str(v)}
        for r, c, v in zip(row_keys, col_keys, vals)
    ]

    return {
        "rows": unique_rows,
        "cols": unique_cols,
        "entries": entries,
    }


def readjson(data: Dict[str, Any]) -> d4m_assoc.Assoc:
    """
    Construct a D4M Assoc from a JSON object in the canonical AA format:
    {
      "rows": [...],
      "cols": [...],
      "entries": [
        {"row": ..., "col": ..., "val": ...},
        ...
      ]
    }

    Args:
        data: A dictionary containing the serialized AA data.

    Returns:
        A new Assoc instance containing all entries described in `data`.

    Raises:
        ValueError: If the input data is missing required keys.
    """
    if "rows" not in data or "cols" not in data or "entries" not in data:
        raise ValueError(
            "Input data must contain 'rows', 'cols', and 'entries' keys."
        )

    # Create an empty Assoc. The row and column labels are defined by the entries,
    # so we don't need to pre-populate them.
    assoc = d4m_assoc.Assoc("", "", "")

    for entry in data["entries"]:
        try:
            row = entry["row"]
            col = entry["col"]
            val = entry["val"]
            assoc.set(row, col, val)
        except KeyError:
            raise ValueError(f"Malformed entry in 'entries' list: {entry}")

    return assoc