from __future__ import annotations

import json
import sys
from pathlib import Path

from app.services.generate_thumbnail import generate_thumbnail_from_script

def main():
    req_path = Path(sys.argv[1])
    payload = json.loads(req_path.read_text(encoding="utf-8"))
    print(f'generate_thumbnail payload: {payload}')
    script = payload["script"]
    seed = payload["seed"]
    # import pdb; pdb.set_trace()

    result: Path = generate_thumbnail_from_script(script, seed)
    print(str(Path(result).resolve()))

if __name__ == "__main__":
    main()
