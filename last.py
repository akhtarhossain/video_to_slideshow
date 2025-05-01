import os
import subprocess
import random
import math

# CONFIG
IMAGE_FOLDER = "clear_scenes"  # Images folder
OUTPUT_VIDEO = "last.mp4"      # Final output video file
BACKGROUND_MUSIC = "voice.mp3" # Background music file
IMAGE_DURATION = 5            # Each image duration in seconds
TOTAL_DURATION = 78          # Total video length in seconds (2h 11m)

def check_requirements():
    # Check images folder
    if not os.path.exists(IMAGE_FOLDER) or not os.path.isdir(IMAGE_FOLDER):
        raise Exception(f"❌ Required image folder not found: {IMAGE_FOLDER}")

    # Check if background music file exists
    if not os.path.exists(BACKGROUND_MUSIC):
        raise Exception(f"❌ Background music file not found: {BACKGROUND_MUSIC}")

def create_slideshow():
    check_requirements()  # Check before starting any processing

    # Read all images from folder
    images = [img for img in os.listdir(IMAGE_FOLDER) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
    
    if not images:
        raise Exception("❌ No images found in clear_scenes folder.")
    
    # Kitni images chahiye?
    images_needed = math.ceil(TOTAL_DURATION / IMAGE_DURATION)
    
    final_images = []
    while len(final_images) < images_needed:
        final_images.append(random.choice(images))  # Randomly select images for repeat

    # Create images.txt for ffmpeg concat
    with open("images.txt", "w") as f:
        for img in final_images:
            f.write(f"file '{os.path.join(IMAGE_FOLDER, img)}'\n")
            f.write(f"duration {IMAGE_DURATION}\n")

    print("🎞️ Creating slideshow video without audio...")

    # Step 1: Create slideshow video WITHOUT audio
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "images.txt",
        "-vf", "zoompan=z='zoom+0.001':d=300:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)',fps=30",
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "temp_video.mp4"
    ], check=True)

    print("✅ Slideshow video created: temp_video.mp4")

    print("🎵 Adding background music...")

    # Step 2: Add background music by looping it
    subprocess.run([
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", BACKGROUND_MUSIC,  # Loop the music infinitely
        "-i", "temp_video.mp4",                        # Input the temp video
        "-shortest",                                   # Cut extra audio if longer than video
        "-c:v", "copy",                                # Don't re-encode video (fast)
        "-c:a", "aac", "-b:a", "192k",                  # Audio settings
        OUTPUT_VIDEO
    ], check=True)

    print(f"✅ Final video created with background music: {OUTPUT_VIDEO}")

    # Step 3: Cleanup temp files
    if os.path.exists("temp_video.mp4"):
        os.remove("temp_video.mp4")

def main():
    try:
        create_slideshow()
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        # Cleanup temp text file
        if os.path.exists("images.txt"):
            os.remove("images.txt")

if __name__ == "__main__":
    main()
