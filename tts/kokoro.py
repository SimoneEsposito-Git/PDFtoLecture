import soundfile as sf
import logging
import numpy as np
from kokoro_onnx import Kokoro
from tts.session import create_session

def tts(text, output_path, voice="af_sarah", speed=1.0, lang="en-us", debug=False):
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
        print(f"Processing text from to audio at {output_path}")

    # Initialize session once and reuse
    session = create_session()
    kokoro = Kokoro.from_session(session, "models/voices-v1.0.bin")

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

def tts_with_timestamps(text, output_path, voice="af_sarah", speed=1.0, lang="en-us", debug=False):
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
        print(f"Generating audio at {output_path}")
        
    # Initialize session and Kokoro model
    session = create_session()
    kokoro = Kokoro.from_session(session, "models/voices-v1.0.bin")

    # Prepare to generate audio
    all_samples = []
    sample_rate = None
    timestamps = []
    current_time = 0.0  # Track the cumulative time in seconds

    # Process each slide
    for slide_data in text.split("\n"):
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
    sf.write(output_path, all_samples, sample_rate)

    if debug:
        print(f"Audio saved at {output_path}")

    return timestamps

import concurrent.futures
from pathlib import Path
from tqdm import tqdm

def tts_parallel(text, output_path, voice="af_sarah", speed=1.0, lang="en-us", debug=False):
    """
    Convert slide-based text to audio files in parallel.

    Args:
        text (str): Text content separated by newlines, each line representing a slide
        output_path (str): Base path for output files
        voice (str): Voice to use for TTS.
        speed (float): Speed of the speech.
        lang (str): Language of the text.
        debug (bool): Whether to print debug information.

    Returns:
        list: A list of file paths to the generated audio files.
    """
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Parse the slides from text and assign numbers
    slides = []
    for i, line in enumerate(text.split('\n')):
        if line.strip():
            slides.append({
                "slide": i+1,  # Start slide numbering from 1
                "text": line.strip()
            })

    def process_slide(slide_data):
        slide_number = slide_data["slide"]
        slide_text = slide_data["text"]
        slide_output_path = output_dir / f"slide_{slide_number}.wav"

        if debug:
            print(f"Processing Slide {slide_number}: {len(slide_text)} characters")

        # Generate audio for the slide
        _, _ = tts(
            slide_text, 
            str(slide_output_path),
            voice=voice, 
            speed=speed, 
            lang=lang, 
            debug=debug
        )

        return slide_output_path

    # Use ThreadPoolExecutor or ProcessPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Create list of futures
        futures = [executor.submit(process_slide, slide) for slide in slides]
        
        # Setup progress bar
        audio_files = []
        total = len(futures)
        
        # Process futures with progress bar
        for future in tqdm(concurrent.futures.as_completed(futures), 
                          total=total, 
                          desc="Converting text to speech",
                          unit="slide"):
            audio_files.append(future.result())

    return audio_files