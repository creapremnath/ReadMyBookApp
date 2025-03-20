import os
import uuid
from PIL import Image
import pytesseract
import boto3
from config import IMAGEDIR,PDFDIR,AUDIODIR,REGION,AWS_SECRET_ACCESS_KEY,AWS_ACCESS_KEY_ID,REGION,TEMPAUDIODIR


# Initialize Polly client
polly =boto3.client("polly",
                    region_name=REGION,
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def image_to_text(path: str, image_name: str) -> str:
    """
    Extract text from an image using pytesseract.
    Args:
        path (str): Directory path of the image.
        image_name (str): Name of the image file.

    Returns:
        str: Extracted text from the image.
    """
    # Automatically detect Tesseract path based on OS
    if os.name == "nt":  # Windows
        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:  # Linux (Docker)
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    try:
        # Path to the image file
        image_path = os.path.join(path, image_name)

        # Read the image using PIL
        image = Image.open(image_path)

        # Extract text from the image
        text = pytesseract.image_to_string(image)

        return text
    except Exception as e:
        return f"Error processing image: {e}"

def text_to_audio(voice:str,text: str,audio_id:str) -> str:
    """
    Convert text to speech using AWS Polly.
    Args:
        text (str): Text to be converted to speech.

    Returns:
        str: Path to the saved audio file.
    """
    try:
        response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice,  # You can change the voice here
            OutputFormat="mp3"
        )

        # Save the audio file
         # Generate a unique filename
        unique_audiofile = f"{audio_id}.mp3"



        audio_file_path = os.path.join(AUDIODIR,unique_audiofile)
        print("audio_file_path",audio_file_path)
        with open(audio_file_path, "wb") as file:
            file.write(response["AudioStream"].read())

        print("Audio file saved to", audio_file_path)
        path_for_html=f"/audios/{unique_audiofile}"
        print("path for html",path_for_html)
        return path_for_html

    except Exception as e:
        return f"Error generating audio: {e}"



TEMPAUDIODIR = os.path.join('static', 'tempaudios')

def text_to_audio2(voice: str, text: str, audio_id: str) -> str:
    """
    Convert text to speech using AWS Polly.
    Args:
        text (str): Text to be converted to speech.
        voice (str): The voice ID for AWS Polly.
        audio_id (str): Unique audio identifier.
    Returns:
        str: Path to the saved audio file.
    """
    try:
        # Ensure the directory exists
        os.makedirs(TEMPAUDIODIR, exist_ok=True)

        # Request speech synthesis from AWS Polly
        response = polly.synthesize_speech(
            Text=text,
            VoiceId=voice,  # Voice for Polly
            OutputFormat="mp3"
        )

        # Unique filename for audio
        print("Problem A")
        unique_audiofile = f"{audio_id}.mp3"

        # Full path where the audio file will be saved
        print("Problem b")
        audio_file_path = os.path.join(TEMPAUDIODIR, unique_audiofile)
        print(audio_file_path)
        print("Problem c")

        # Write audio data to the file
        with open(audio_file_path, "wb") as file:
            print("Problem d")
            file.write(response["AudioStream"].read())

        # Return the relative path for use in HTML or further processing

        return audio_file_path

    except Exception as e:
        # Return error message if something goes wrong
        return f"Error generating audio: {e}"
