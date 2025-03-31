import soundfile as sf
import logging
import numpy as np
from kokoro_onnx import Kokoro
from tts.session import create_session

def tts(input_path, output_path, voice="af_sarah", speed=1.0, lang="en-us", debug=False):
    """
    Convert text from input_path to speech saved at output_path.

    Args:
        input_path (str): Path to the text file to convert.
        output_path (str): Path where the audio will be saved.
        voice (str): Voice to use for TTS.
        speed (float): Speed of the speech.
        lang (str): Language of the text.
        debug (bool): Whether to print debug information.

    Returns:
        tuple: (samples, sample_rate) of the generated audio.
    """
    # Set logging level based on debug flag
    log_level = logging.DEBUG if debug else logging.WARNING
    logging.getLogger("kokoro_onnx").setLevel(log_level)

    if debug:
        print(f"Processing text from {input_path} to audio at {output_path}")

    # Initialize session once and reuse
    session = create_session()
    kokoro = Kokoro.from_session(session, "models/voices-v1.0.bin")

    # Read text file
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    if debug:
        print(f"Read {len(text)} characters from {input_path}")

    # Generate speech
    samples, sample_rate = kokoro.create(
        text, voice=voice, speed=speed, lang=lang
    )

    # Use float32 explicitly for better performance
    samples = np.array(samples, dtype=np.float32)

    # Write output
    sf.write(output_path, samples, sample_rate)

    if debug:
        print(f"Created audio at {output_path}")

    return samples, sample_rate

def tts_with_timestamps(input_text, output_audio_path, voice="af_sarah", speed=1.0, lang="en-us", debug=False):
    """
    Convert slide-based text to a single audio file with timestamps for each slide.

    Args:
        input_text (list): A list of dictionaries, where each dictionary contains:
            - "slide": Slide number
            - "text": Text content for the slide
        output_audio_path (str): Path to save the generated audio file.
        voice (str): Voice to use for TTS.
        speed (float): Speed of the speech.
        lang (str): Language of the text.
        debug (bool): Whether to print debug information.

    Returns:
        dict: A dictionary containing timestamps for each slide.
    """
    # Set logging level based on debug flag
    log_level = logging.DEBUG if debug else logging.WARNING
    logging.getLogger("kokoro_onnx").setLevel(log_level)

    if debug:
        print(f"Generating audio at {output_audio_path}")

    # Initialize session and Kokoro model
    session = create_session()
    kokoro = Kokoro.from_session(session, "models/voices-v1.0.bin")

    # Prepare to generate audio
    all_samples = []
    sample_rate = None
    timestamps = []
    current_time = 0.0  # Track the cumulative time in seconds

    # Process each slide
    for slide_data in input_text:
        slide_number = slide_data["slide"]
        slide_text = slide_data["text"]

        if debug:
            print(f"Processing Slide {slide_number}: {len(slide_text)} characters")

        # Generate audio for the slide
        samples, sample_rate = kokoro.create(
            slide_text, voice=voice, speed=speed, lang=lang
        )

        # Append the samples to the full audio
        all_samples.extend(samples)

        # Record the timestamp for this slide
        duration = len(samples) / sample_rate  # Duration of the slide in seconds
        timestamps.append({
            "slide": slide_number,
            "start_time": current_time,
            "end_time": current_time + duration
        })
        current_time += duration

    # Save the combined audio to the output file
    all_samples = np.array(all_samples, dtype=np.float32)
    sf.write(output_audio_path, all_samples, sample_rate)

    if debug:
        print(f"Audio saved at {output_audio_path}")

    return timestamps