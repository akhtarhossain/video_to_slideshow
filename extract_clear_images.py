import os
import cv2
import shutil
import subprocess
import numpy as np
from skimage.metrics import structural_similarity as ssim

INPUT_VIDEO = "input.mp4"
RAW_FRAMES_DIR = "raw_frames"
CLEAR_FRAMES_DIR = "clear_scenes"
SCENE_TIMESTAMPS_FILE = "scene_timestamps.txt"

def run_scene_detection():
    """Detect scenes and save timestamps."""
    if os.path.exists(SCENE_TIMESTAMPS_FILE):
        os.remove(SCENE_TIMESTAMPS_FILE)

    print("🔍 Detecting scene changes...")
    result = subprocess.run([
        'ffmpeg', '-i', INPUT_VIDEO,
        '-filter_complex', 'select=gt(scene\\,0.2),metadata=print',
        '-an', '-f', 'null', '-'
    ], stderr=subprocess.PIPE, text=True)

    timestamps = []
    for line in result.stderr.splitlines():
        if "pts_time:" in line:
            try:
                time_str = line.split("pts_time:")[1].strip().split()[0]
                timestamps.append(float(time_str))
            except (IndexError, ValueError):
                continue

    with open(SCENE_TIMESTAMPS_FILE, "w") as f:
        for ts in timestamps:
            f.write(f"{ts}\n")
    print(f"✅ Found {len(timestamps)} scenes.")

def extract_multiple_frames(frames_per_scene=10):
    """Extract multiple frames around each scene timestamp."""
    if os.path.exists(RAW_FRAMES_DIR):
        shutil.rmtree(RAW_FRAMES_DIR)
    os.makedirs(RAW_FRAMES_DIR)

    with open(SCENE_TIMESTAMPS_FILE, "r") as f:
        timestamps = [float(line.strip()) for line in f.readlines()]

    print(f"🖼️ Extracting {frames_per_scene} frames per scene...")

    for idx, ts in enumerate(timestamps):
        scene_folder = os.path.join(RAW_FRAMES_DIR, f"scene_{idx:04d}")
        os.makedirs(scene_folder, exist_ok=True)

        for i in range(frames_per_scene):
            offset = i * 0.2  # 0.2 sec difference between frames
            capture_time = ts + offset
            output_filename = os.path.join(scene_folder, f"img_{i:02d}.jpg")

            subprocess.run([
                'ffmpeg', '-ss', str(capture_time),
                '-i', INPUT_VIDEO,
                '-frames:v', '1',
                '-q:v', '2',
                '-vf', 'scale=1280:-1',  # 1280px width, auto height
                output_filename,
                '-y'
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    print(f"✅ Frames extracted for {len(timestamps)} scenes.")

def is_blurry(image_path, threshold=100.0):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    score = laplacian.var()
    return score < threshold

def is_black(image_path, threshold=10):
    image = cv2.imread(image_path)
    return np.mean(image) < threshold

def select_best_image(scene_folder):
    """Select best image from a scene folder."""
    images = sorted(os.listdir(scene_folder))
    best_score = -1
    best_image = None

    for img in images:
        img_path = os.path.join(scene_folder, img)

        if is_black(img_path) or is_blurry(img_path):
            continue

        # Higher Laplacian variance = sharper image
        image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        laplacian = cv2.Laplacian(image, cv2.CV_64F)
        score = laplacian.var()

        if score > best_score:
            best_score = score
            best_image = img_path

    return best_image

def filter_best_images():
    """From each scene, pick the best clear image."""
    if os.path.exists(CLEAR_FRAMES_DIR):
        shutil.rmtree(CLEAR_FRAMES_DIR)
    os.makedirs(CLEAR_FRAMES_DIR)

    scenes = sorted(os.listdir(RAW_FRAMES_DIR))

    saved_count = 0
    for idx, scene in enumerate(scenes):
        scene_folder = os.path.join(RAW_FRAMES_DIR, scene)
        if not os.path.isdir(scene_folder):
            continue

        best_image = select_best_image(scene_folder)
        if best_image:
            shutil.copy(best_image, os.path.join(CLEAR_FRAMES_DIR, f"scene_{idx:04d}.jpg"))
            saved_count += 1

    print(f"✅ Saved {saved_count} best clear images (one per scene).")

def main():
    print("🎬 Starting fast full HD clear image extraction process...\n")
    if not os.path.exists(INPUT_VIDEO):
        print(f"❌ Input video not found: {INPUT_VIDEO}")
        return
    run_scene_detection()
    extract_multiple_frames(frames_per_scene=10)
    filter_best_images()
    print("\n🧹 Done!")

if __name__ == "__main__":
    main()
