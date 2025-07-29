import json
from pathlib import Path

def write_to_temp_json(data: dict, filename: str = "temp.json") -> None:
    """
    Writes the given dictionary to a JSON file.

    Args:
        data (dict): Data to write to JSON.
        filename (str): Name of the file. Defaults to 'temp.json'.
    """
    file_path = Path(__file__).parent / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Data written to {file_path}")
