import os
import random
import subprocess

IMAGES_DIR = "clear_scenes"
OUTPUT_VIDEO = "loading1.mp4"
DURATION_PER_IMAGE = 14  # seconds
TOTAL_DURATION = 8100    # seconds (20 minutes)
NUM_IMAGES = TOTAL_DURATION // DURATION_PER_IMAGE

def generate_image_list():
    try:
        all_images = sorted(os.listdir(IMAGES_DIR))
        if len(all_images) == 0:
            raise FileNotFoundError(f"❌ No images found in {IMAGES_DIR}.")
    
        selected_images = [random.choice(all_images) for _ in range(NUM_IMAGES)]
        with open("slideshow_list.txt", "w") as f:
            for img in selected_images:
                f.write(f"file '{os.path.join(IMAGES_DIR, img)}'\n")
                f.write(f"duration {DURATION_PER_IMAGE}\n")
            f.write(f"file '{os.path.join(IMAGES_DIR, selected_images[-1])}'\n")
        print("✅ Slideshow list created.")
    except FileNotFoundError as e:
        print(e)
        raise

def create_video():
    try:
        # FFmpeg command to create slideshow video with random images repeating
        result = subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "slideshow_list.txt",
            "-t", str(TOTAL_DURATION), "-c:v", "libx264", "-pix_fmt", "yuv420p", OUTPUT_VIDEO
        ], capture_output=True, text=True)

        if result.returncode != 0:
            raise Exception(f"❌ FFmpeg command failed with error:\n{result.stderr}")
        
        print(f"✅ Slideshow created: {OUTPUT_VIDEO}")
    
    except Exception as e:
        print(f"⚠️ Error: {e}")
        print(f"❌ FFmpeg Output: {result.stderr}")

def main():
    try:
        generate_image_list()
        create_video()
    except Exception as e:
        print(f"⚠️ Error during process: {e}")
    finally:
        if os.path.exists("slideshow_list.txt"):
            os.remove("slideshow_list.txt")

if __name__ == "__main__":
    main()
