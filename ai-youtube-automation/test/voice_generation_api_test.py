"""
python -m pytest test/voice_generation_api_test.py
"""

import os
from app.services.generate_voice import generate_voice

def test_generate_voice():
    input_text = "Hello, this is a test of the voice generation API."
    input_path = "test_input.txt"
    output_path = "test_output/voice.mp3"

    # Write test input to a file
    with open(input_path, "w", encoding="utf-8") as f:
        f.write(input_text)

    # Generate voice
    generated_path = generate_voice(script_path=input_path, output_path=output_path)

    # Check if output file exists
    assert os.path.exists(generated_path), "Output MP3 file was not created."

    # Clean up test files
    # os.remove(input_path)
    # os.remove(generated_path)