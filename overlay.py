import os
import subprocess

# Configuration
IMAGES_DIR = "all"
OUTPUT_VIDEO = "promotion.mp4"
OVERLAY_VIDEO = "complete.mp4"
FINAL_VIDEO = "overlay.mp4"
DURATION_PER_IMAGE = 15
NUM_IMAGES =66

def generate_image_list():
    all_images = sorted(os.listdir(IMAGES_DIR))
    selected_images = [img for img in all_images if img.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if len(selected_images) != NUM_IMAGES:
        raise Exception(f"❌ Expected {NUM_IMAGES} images, found {len(selected_images)} valid images.")

    with open("slideshow_list.txt", "w") as f:
        for img in selected_images:
            f.write(f"file '{os.path.join(IMAGES_DIR, img)}'\n")
            f.write(f"duration {DURATION_PER_IMAGE}\n")
        f.write(f"file '{os.path.join(IMAGES_DIR, selected_images[-1])}'\n")
    print("✅ Slideshow list created.")

def create_video():
    print("🎞️ Creating slideshow video...")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "slideshow_list.txt",
        "-vf", "scale=1280:720,fps=25",
        "-pix_fmt", "yuv420p",
        "-c:v", "libx264",
        "-preset", "fast",  # Changed from medium to fast
        "-crf", "23",
        "-threads", "2",  # Limit threads to reduce memory
        OUTPUT_VIDEO
    ], check=True)
    print(f"✅ Slideshow created: {OUTPUT_VIDEO}")

def overlay_green_screen():
    print("🟩 Overlaying green screen video...")
    
    # Get duration of promotion video
    result = subprocess.run([
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        OUTPUT_VIDEO
    ], capture_output=True, text=True)
    promo_duration = float(result.stdout.strip())
    
    # Build optimized filter chain
    filter_complex = (
        f"[1:v]scale=1280:720,fps=25,format=yuva420p,"  # Changed to yuva420p
        f"colorkey=0x41CE43:0.3:0.2[overlay];"
        f"[0:v][overlay]overlay=shortest=1"
    )
    
    subprocess.run([
        "ffmpeg", "-y",
        "-i", OUTPUT_VIDEO,
        "-stream_loop", "-1",
        "-i", OVERLAY_VIDEO,
        "-filter_complex", filter_complex,
        "-c:v", "libx264",
        "-preset", "fast",  # Changed from medium to fast
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-threads", "2",  # Limit threads to reduce memory
        "-t", str(promo_duration),
        "-movflags", "+faststart",
        FINAL_VIDEO
    ], check=True)
    print(f"✅ Final video created: {FINAL_VIDEO}")

def main():
    try:
        generate_image_list()
        create_video()
        overlay_green_screen()
    except subprocess.CalledProcessError as e:
        print(f"⚠️ FFmpeg error: {e.stderr}")
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        if os.path.exists("slideshow_list.txt"):
            os.remove("slideshow_list.txt")

if __name__ == "__main__":
    main()