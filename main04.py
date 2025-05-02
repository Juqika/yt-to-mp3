import os
import sys
import subprocess
import shutil
import argparse

# Memeriksa dan menginstall yt_dlp jika belum ada
try:
    import yt_dlp
except ImportError:
    print("yt_dlp belum terinstall. Mencoba menginstall...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        print("yt_dlp berhasil terinstall.")
        import yt_dlp  # Mengimport setelah instalasi
    except subprocess.CalledProcessError:
        print("Gagal menginstall yt_dlp. Silakan install manual dengan 'pip install yt-dlp'.")
        exit(1)

# Menentukan direktori untuk menyimpan hasil download
downloads_dir = 'downloads'

# Membuat direktori downloads jika belum ada
if not os.path.exists(downloads_dir):
    os.makedirs(downloads_dir)

# Mengatur parser untuk argumen opsional lokasi ffmpeg
parser = argparse.ArgumentParser(description='Konverter YouTube ke MP3')
parser.add_argument('--ffmpeg-location', help='Path ke executable ffmpeg')
args = parser.parse_args()

# Menentukan path ffmpeg
if args.ffmpeg_location:
    if not os.path.exists(args.ffmpeg_location):
        print(f"Error: Lokasi ffmpeg yang ditentukan '{args.ffmpeg_location}' tidak ada.")
        exit(1)
    ffmpeg_path = args.ffmpeg_location
else:
    ffmpeg_path = shutil.which('ffmpeg')
    if not ffmpeg_path:
        predefined_path = r'C:\ffmpeg\bin\ffmpeg.exe'  # Ubah sesuai kebutuhan
        if os.path.exists(predefined_path):
            ffmpeg_path = predefined_path
        else:
            print("Error: ffmpeg tidak ditemukan. Install ffmpeg dan pastikan ada di PATH atau berikan path dengan --ffmpeg-location.")
            print("Instruksi instalasi:")
            print("- Windows: Unduh dari https://ffmpeg.org/download.html dan tambahkan ke PATH")
            print("- macOS: Jalankan `brew install ffmpeg`")
            print("- Linux: Jalankan `sudo apt-get install ffmpeg` (Ubuntu) atau setara")
            exit(1)

print(f"Menggunakan ffmpeg dari: {ffmpeg_path}")

# Meminta pengguna memasukkan URL YouTube
url = input("Masukkan URL video atau playlist YouTube: ")

# Mengatur opsi untuk yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',  # Memilih kualitas audio terbaik
    'postprocessors': [{  # Mengekstrak audio dan mengkonversi ke MP3
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '0',  # Kualitas terbaik
    }, {
        'key': 'EmbedThumbnail',  # Menyematkan thumbnail video sebagai cover
    }, {
        'key': 'FFmpegMetadata',  # Menyematkan metadata
    }],
    'outtmpl': os.path.join(downloads_dir, '%(title)s.%(ext)s'),  # Template output
    'ffmpeg_location': ffmpeg_path,  # Menggunakan path ffmpeg yang ditentukan
}

# Mendownload audio
try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Download selesai.")
except Exception as e:
    print(f"Terjadi kesalahan: {e}")