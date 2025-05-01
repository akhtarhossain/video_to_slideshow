import os
import subprocess

IMAGES_DIR = "all"  # Folder containing the images
OUTPUT_VIDEO = "promotion.mp4"  # Output video name
DURATION_PER_IMAGE = 6  # Duration per image in seconds
NUM_IMAGES = 6  # Total number of images (as you mentioned)

def generate_image_list():
    all_images = sorted(os.listdir(IMAGES_DIR))
    if len(all_images) != NUM_IMAGES:
        raise Exception(f"❌ Expected {NUM_IMAGES} images, but found {len(all_images)} images.")

    selected_images = [img for img in all_images if img.endswith(('jpg', 'jpeg', 'png'))]  # Ensuring image files
    if len(selected_images) != NUM_IMAGES:
        raise Exception("❌ Not enough valid images found.")

    with open("slideshow_list.txt", "w") as f:
        for img in selected_images:
            f.write(f"file '{os.path.join(IMAGES_DIR, img)}'\n")
            f.write(f"duration {DURATION_PER_IMAGE}\n")
        # Repeat the last image to avoid ffmpeg bug
        f.write(f"file '{os.path.join(IMAGES_DIR, selected_images[-1])}'\n")
    print("✅ Slideshow list created.")

def create_video():
    print("🎞️ Generating slideshow video...")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "slideshow_list.txt",
                        "-vf", "scale=1280:720",
        "-vsync", "vfr", "-pix_fmt", "yuv420p", OUTPUT_VIDEO
    ], check=True)
    print(f"✅ Slideshow created: {OUTPUT_VIDEO}")

def main():
    try:
        generate_image_list()
        create_video()
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        if os.path.exists("slideshow_list.txt"):
            os.remove("slideshow_list.txt")

if __name__ == "__main__":
    main()
