import yt_dlp
import os
from pydub import AudioSegment
# Downloaded audio ko store karne ke liye folder
DOWNLOAD_DIR = "downloads"

# Agar downloads folder exist nahi karta to create kar do
# Agar pehle se hai to error mat do
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def download_youtube_audio(url: str) -> str:

    # Download hone wali file ka path aur naam set kar rahe hain
    # %(title)s -> YouTube video ka title
    # %(ext)s -> Original extension (webm, m4a, etc.)
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    # yt_dlp ki settings
    ydl_opts = {

        # Best quality audio download karo
        "format": "bestaudio/best",

        # File kis location par save hogi
        "outtmpl": output_path,

        # Download ke baad audio ko process karo
        "postprocessors": [
            {
                # FFmpeg use karke sirf audio extract karo
                "key": "FFmpegExtractAudio",

                # Audio ko WAV format me convert karo
                "preferredcodec": "wav",

                # Audio quality 192 kbps rakho
                "preferredquality": "192",
            }
        ],

        # Terminal me unnecessary messages mat print karo
        "quiet": True,
    }

    # yt_dlp object banao aur diye gaye settings use karo
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        # URL se audio download karo aur video ki information le lo
        info = ydl.extract_info(url, download=True)

        # Download hui file ka naam/path nikal lo
        filename = ydl.prepare_filename(info)

        # Agar extension .webm ya .m4a hai to usse .wav bana do
        filename = filename.replace(".webm", ".wav").replace(".m4a", ".wav")

    # Final WAV file ka path return kar do
    return filename






def convert_to_wav(input_path: str) -> str:
    """
    Kisi bhi audio/video file ko WAV format me convert karta hai.
    Output audio mono (1 channel) aur 16 kHz sample rate me save hoti hai.
    """

    # Input file ka extension (.mp3, .mp4, etc.) hata kar
    # uske end me "_converted.wav" add kar dete hain.
    # Example:
    # input_path = "songs/music.mp3"
    # output_path = "songs/music_converted.wav"
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    # Input file ko pydub ki help se load karte hain.
    # Ye MP3, MP4, WAV, M4A, etc. sab read kar sakta hai.
    audio = AudioSegment.from_file(input_path)

    # Audio ko standard format me convert karte hain:
    # set_channels(1) -> Stereo se Mono bana deta hai.
    # set_frame_rate(16000) -> Sample rate 16 kHz kar deta hai.
    # Speech-to-Text models (Whisper, DeepSpeech, etc.) ke liye ye best hota hai.
    audio = audio.set_channels(1).set_frame_rate(16000)

    # Converted audio ko WAV format me save kar dete hain.
    audio.export(output_path, format="wav")

    # Nayi WAV file ka path return kar dete hain.
    return output_path




def chunk_audio(wav_path:str,chunk_minutes:int =10)-> list:
    audio=AudioSegment.from_wav(wav_path)
    chunk_ms=chunk_minutes*60*1000;

    chunks=[]

    for i,start in enumerate (range(0,len(audio),chunk_ms)):
        chunk=audio[start:start+chunk_ms]
        chunk_path=f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path,format="wav")

        chunks.append(chunk_path)

    return chunks;





def process_input(source: str) -> list:

    # Check if the input is a URL
    if source.startswith("http://") or source.startswith("https://"):

        print("Detected YouTube URL. Downloading audio...")

        # Download YouTube audio
        wav_path = download_youtube_audio(source)

    else:

        print("Detected local file. Converting to WAV...")

        # Convert local audio/video to WAV
        wav_path = convert_to_wav(source)

    print("Chunking audio...")

    # Split audio into chunks
    chunks = chunk_audio(wav_path)

    print(f"Audio ready - {len(chunks)} chunk(s) created.")

    return chunks


