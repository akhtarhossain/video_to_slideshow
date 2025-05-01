import os
import subprocess

# Input videos
VIDEOS = ["trailer.mp4", "promotion.mp4"]
FINAL_OUTPUT = "start.mp4"
MERGE_LIST = "videos.txt"

def check_files_exist():
    for video in VIDEOS:
        if not os.path.exists(video):
            raise FileNotFoundError(f"❌ File not found: {video}")

def convert_to_hd(input_file, output_file):
    """Convert video to HD 1080p with consistent audio/video format"""
    print(f"🎬 Converting {input_file} to HD...")
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file,
        "-vf", "scale=-1:1080",  # Scale height to 1080p, keep aspect ratio
        "-r", "30",              # 30 FPS
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        output_file
    ], check=True)

def merge_videos():
    converted_files = []

    try:
        # Step 1: Convert both videos to normalized HD format
        for i, video in enumerate(VIDEOS):
            out_file = f"hd_{i}.mp4"
            convert_to_hd(video, out_file)
            converted_files.append(out_file)

        # Step 2: Create text file for FFmpeg concat
        with open(MERGE_LIST, "w") as f:
            for file in converted_files:
                f.write(f"file '{file}'\n")

        # Step 3: Concatenate videos
        print("🔗 Merging videos...")
        subprocess.run([
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", MERGE_LIST,
            "-c", "copy", FINAL_OUTPUT
        ], check=True)

        print(f"\n✅ Merged video saved as: {FINAL_OUTPUT}")

    finally:
        # Cleanup temporary files
        for file in converted_files:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(MERGE_LIST):
            os.remove(MERGE_LIST)

if __name__ == "__main__":
    try:
        check_files_exist()
        merge_videos()
    except Exception as e:
        print(f"❌ Error: {e}")
