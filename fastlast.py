import os
import subprocess
import random
import math

# CONFIGURATION
IMAGE_FOLDER = "clear_scenes"      # Folder jahan images hain
OUTPUT_VIDEO = "last.mp4"          # Final output video name
BACKGROUND_MUSIC = "voice.mp3"     # Background music file
IMAGE_DURATION = 10                # Har image ka duration (seconds)
TOTAL_DURATION = 7860              # Total video duration in seconds

def create_slideshow():
    # Read all images from folder
    images = [img for img in os.listdir(IMAGE_FOLDER) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
    if not images:
        raise Exception("❌ No images found in clear_scenes folder.")

    # Kitni images chahiye?
    images_needed = math.ceil(TOTAL_DURATION / IMAGE_DURATION)

    # Randomly repeat images
    final_images = []
    while len(final_images) < images_needed:
        final_images.append(random.choice(images))

    # Create concat input file for ffmpeg
    with open("images.txt", "w") as f:
        for img in final_images:
            f.write(f"file '{os.path.join(IMAGE_FOLDER, img)}'\n")
            f.write(f"duration {IMAGE_DURATION}\n")

    print("🎞️ Creating fast slideshow video (no zoom)...")

    # Step 1: Create slideshow video WITHOUT zoom/pan
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "images.txt",
        "-vf", "format=yuv420p",     # Simple fast slideshow
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "temp_video.mp4"
    ], check=True)

    print("✅ Slideshow created: temp_video.mp4")

    print("🎵 Adding background music...")

    # Step 2: Add background music by looping it to match video
    subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", BACKGROUND_MUSIC,  # Loop background music
        "-i", "temp_video.mp4",                        # Input video
        "-shortest",                                   # Trim audio if longer
        "-c:v", "copy",                                # No re-encode
        "-c:a", "aac", "-b:a", "192k",                 # Audio quality
        OUTPUT_VIDEO
    ], check=True)

    print(f"✅ Final video created: {OUTPUT_VIDEO}")

    # Cleanup
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
