import os
import subprocess
import random
import math
from tqdm import tqdm

# CONFIGURATION
IMAGE_FOLDER = "clear_scenes"
OUTPUT_VIDEO = "last.mp4"
BACKGROUND_MUSIC = "voice.mp3"
IMAGE_DURATION = 10  # Each image duration = 10 seconds (reduced from 20)
TOTAL_DURATION = 5360  # Total video duration in seconds (e.g. 2 hours 10 sec)

def check_requirements():
    if not os.path.exists(IMAGE_FOLDER) or not os.path.isdir(IMAGE_FOLDER):
        raise Exception(f"❌ Required image folder not found: {IMAGE_FOLDER}")
    if not os.path.exists(BACKGROUND_MUSIC):
        raise Exception(f"❌ Background music file not found: {BACKGROUND_MUSIC}")

def create_slideshow():
    check_requirements()

    images = [img for img in os.listdir(IMAGE_FOLDER) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        raise Exception("❌ No images found in clear_scenes folder.")

    images_needed = math.ceil(TOTAL_DURATION / IMAGE_DURATION)
    final_images = []

    print(f"🧮 Generating {images_needed} images with random repetition...\n")
    for _ in tqdm(range(images_needed), desc="📸 Selecting images"):
        final_images.append(random.choice(images))

    # Create images.txt file for FFmpeg
    with open("images.txt", "w") as f:
        for img in final_images[:-1]:  # all except last
            f.write(f"file '{os.path.join(IMAGE_FOLDER, img)}'\n")
            f.write(f"duration {IMAGE_DURATION}\n")
        f.write(f"file '{os.path.join(IMAGE_FOLDER, final_images[-1])}'\n")  # last image, no duration

    print("🎞️ Creating slideshow video with zoom effect...")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "images.txt",
        "-vf", "scale=1280:720,zoompan=z='zoom+0.0005':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',fps=30", # Reduced zoom speed (d)
        "-c:v", "libx264", "-preset", "faster", "-pix_fmt", "yuv420p", # Added faster preset
        "temp_video.mp4"
    ], check=True)

    print("✅ Slideshow video created: temp_video.mp4")
    print("🎵 Adding background music (looped and trimmed)...")

    subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", BACKGROUND_MUSIC,  # loop music if needed
        "-i", "temp_video.mp4",
        "-shortest",  # cut audio to match video
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-ar", "48000", "-ac", "2",
        OUTPUT_VIDEO
    ], check=True)

    print(f"✅ Final video created with background music: {OUTPUT_VIDEO}")

    # Cleanup
    if os.path.exists("temp_video.mp4"):
        os.remove("temp_video.mp4")

def main():
    try:
        create_slideshow()
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        if os.path.exists("images.txt"):
            os.remove("images.txt")

if __name__ == "__main__":
    main()