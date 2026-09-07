@echo off
setlocal
poetry run python -m ml.generate_data || exit /b 1
poetry run python -m ml.train --tracking local || exit /b 1
poetry run python -m ml.compare_runs || exit /b 1
poetry run python -m ml.score --tracking local || exit /b 1
poetry run python -m ml.verify_poc --tracking local || exit /b 1
poetry run pytest -q || exit /b 1
echo [SUCCESS] Local POC-07 Poetry smoke test complete.
