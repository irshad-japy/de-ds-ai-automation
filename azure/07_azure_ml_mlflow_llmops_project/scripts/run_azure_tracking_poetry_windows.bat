@echo off
setlocal
poetry run python -m ml.verify_config || exit /b 1
poetry run python -m ml.generate_data || exit /b 1
poetry run python -m ml.register_data || exit /b 1
poetry run python -m ml.train --tracking azure || exit /b 1
poetry run python -m ml.compare_runs || exit /b 1
poetry run python -m ml.register_model --tracking azure || exit /b 1
poetry run python -m ml.score --tracking azure || exit /b 1
poetry run python -m ml.verify_poc --tracking azure --check-registry || exit /b 1
echo [SUCCESS] Azure ML tracking/registry POC-07 Poetry validation complete.
