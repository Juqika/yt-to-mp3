import os
import sys
import subprocess
import shutil
import threading

# Check and install FreeSimpleGUI if not present
try:
    import FreeSimpleGUI as sg
except ImportError:
    print("FreeSimpleGUI not installed. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "FreeSimpleGUI"])
        print("FreeSimpleGUI installed successfully.")
        import FreeSimpleGUI as sg
    except subprocess.CalledProcessError:
        print("Failed to install FreeSimpleGUI. Please install manually with 'pip install FreeSimpleGUI'.")
        exit(1)

# Check and install yt_dlp if not present
try:
    import yt_dlp
except ImportError:
    print("yt_dlp not installed. Attempting to install...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        print("yt_dlp installed successfully.")
        import yt_dlp
    except subprocess.CalledProcessError:
        print("Failed to install yt_dlp. Please install manually with 'pip install yt-dlp'.")
        exit(1)

# Create downloads directory if it doesn't exist
if not os.path.exists('downloads'):
    os.makedirs('downloads')

# Define the GUI layout
layout = [
    [sg.Text("YouTube URL:")],
    [sg.Input(key='-URL-')],
    [sg.Text("Output format:")],
    [sg.Radio("MP3 (320 kbps)", "FORMAT", default=True, key='-MP3-'), sg.Radio("WAV", "FORMAT", key='-WAV-')],
    [sg.Button("Download"), sg.Button("Open Downloads Folder"), sg.Button("Exit")],
    [sg.Multiline(size=(60, 10), key='-STATUS-', disabled=True)]
]

# Create the window
window = sg.Window("YouTube to Audio Converter", layout)
downloading = False

def download(url, format, window):
    # Determine ffmpeg path
    ffmpeg_path = None
    if hasattr(sys, '_MEIPASS'):
        ffmpeg_path = os.path.join(sys._MEIPASS, 'ffmpeg', 'bin', 'ffmpeg.exe')
        if not os.path.exists(ffmpeg_path):
            window.write_event_value('-ERROR-', f"FFmpeg not found in bundled path: {ffmpeg_path}. Ensure ffmpeg/bin/ffmpeg.exe is included.")
            return
    else:
        ffmpeg_path = shutil.which('ffmpeg')
        if not ffmpeg_path:
            window.write_event_value('-ERROR-', "FFmpeg not found in PATH. Please install FFmpeg and add it to your PATH.")
            return

    ydl_opts = {
        'format': 'bestaudio/best',  # Select best audio quality
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': format,
            'preferredquality': '320' if format == 'mp3' else None,  # 320 kbps for MP3
        }, {
            'key': 'FFmpegMetadata',  # Embed metadata
        }],
        'outtmpl': os.path.join('downloads', '%(title)s.%(ext)s'),  # Output template
        'ffmpeg_location': ffmpeg_path,  # Use determined ffmpeg path
        'progress_hooks': [lambda d: progress_hook(d, window)],
    }

    if format == 'mp3':
        ydl_opts['postprocessors'].insert(1, {'key': 'EmbedThumbnail'})  # Embed thumbnail for MP3

    def progress_hook(d, window):
        if d['status'] == 'downloading':
            message = f"Downloading: {d['_percent_str']}"
        elif d['status'] == 'finished':
            message = "Processing..."
        else:
            message = d['status']
        window.write_event_value('-PROGRESS-', message)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        window.write_event_value('-FINISHED-', None)
    except Exception as e:
        window.write_event_value('-ERROR-', str(e))

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Download':
        if downloading:
            sg.popup("A download is already in progress.")
            continue
        url = values['-URL-']
        if not url:
            sg.popup("Please enter a YouTube URL.")
            continue
        format = 'mp3' if values['-MP3-'] else 'wav'
        downloading = True
        threading.Thread(target=download, args=(url, format, window), daemon=True).start()
    elif event == 'Open Downloads Folder':
        if os.name == 'nt':  # Windows
            os.startfile('downloads')
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', 'downloads'])
        else:  # Linux
            subprocess.call(['xdg-open', 'downloads'])
    elif event == '-PROGRESS-':
        window['-STATUS-'].update(values['-PROGRESS-'] + '\n', append=True)
    elif event == '-FINISHED-':
        downloading = False
        window['-STATUS-'].update("Download completed.\n", append=True)
    elif event == '-ERROR-':
        downloading = False
        sg.popup("Error", values['-ERROR-'])

window.close()