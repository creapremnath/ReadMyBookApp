from pydub import AudioSegment
import os

def merge_mp3(files, output_file):
    """
    Merges multiple MP3 files into a single MP3 file.
    
    :param files: List of MP3 file paths to merge.
    :param output_file: Path to save the merged MP3 file.
    """
    # Start with an empty audio segment
    combined = AudioSegment.empty()

    # Loop through each file and add it to the combined audio
    for file in files:
        audio = AudioSegment.from_mp3(file)  # Read the MP3 file
        combined += audio  # Concatenate the audio

    # Export the final combined audio to an MP3 file
    combined.export(f"static/audios/{output_file}.mp3", format="mp3")
    final_file = f"audios/{output_file}.mp3"  # Ensure this matches what you want to return
    for i in files:
        # Delete the temporary MP3 file
        os.remove(i)

    print(f"Successfully merged audio files into {final_file}")
    return final_file
