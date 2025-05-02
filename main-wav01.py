import os
import sys
import subprocess
import shutil
import argparse

# Check and install yt_dlp if not present
try:
    import yt_dlp
except ImportError:
    print("yt_dlp not installed. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        print("yt_dlp installed successfully.")
        import yt_dlp  # Import after installation
    except subprocess.CalledProcessError:
        print("Failed to install yt_dlp. Please install manually with 'pip install yt-dlp'.")
        exit(1)

# Define the directory for downloads
downloads_dir = 'downloads'

# Create downloads directory if it doesn't exist
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

# Set up argument parser for optional ffmpeg location
parser = argparse.ArgumentParser(description='YouTube to WAV converter')
parser.add_argument('--ffmpeg-location', help='Path to ffmpeg executable')
args = parser.parse_args()

# Determine ffmpeg path
if args.ffmpeg_location:
    if not os.path.exists(args.ffmpeg_location):
        print(f"Error: Specified ffmpeg location '{args.ffmpeg_location}' does not exist.")
        exit(1)
    ffmpeg_path = args.ffmpeg_location
else:
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        predefined_path = r'C:\ffmpeg\bin\ffmpeg.exe'  # Modify as needed
        if os.path.exists(predefined_path):
            ffmpeg_path = predefined_path
        else:
            print("Error: ffmpeg not found. Please install ffmpeg and ensure it's in your PATH or provide the path using --ffmpeg-location.")
            exit(1)

print(f"Using ffmpeg from: {ffmpeg_path}")

# Prompt user for YouTube URL
url = input("Enter YouTube video or playlist URL: ")

# Set up yt-dlp options for WAV output
ydl_opts = {
    'format': 'bestaudio/best',  # Select best audio quality
    'postprocessors': [{  # Extract audio and convert to WAV
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'wav',  # Change to WAV
    }, {
        'key': 'FFmpegMetadata',  # Embed metadata (if supported)
    }],
    'outtmpl': os.path.join(downloads_dir, '%(title)s.wav'),  # Output template with .wav extension
    'ffmpeg_location': ffmpeg_path,  # Use determined ffmpeg path
}

# Download the audio
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Download completed.")
except Exception as e:
    print(f"An error occurred: {e}")