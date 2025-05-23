import os
import subprocess

# Input videos
VIDEOS_TO_MERGE = ["final_output1.mp4", "last.mp4"]
FINAL_VIDEO = "final_output.mp4"
TEMP_FILE = "temp_list.txt"

def check_videos_exist():
    missing_videos = [v for v in VIDEOS_TO_MERGE if not os.path.exists(v)]
    if missing_videos:
        raise FileNotFoundError(f"❌ Missing files: {', '.join(missing_videos)}")

def get_video_duration(filename):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filename
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise Exception(f"Couldn't get duration for {filename}: {result.stderr}")
    return float(result.stdout.strip())

def merge_videos_directly():
    print("🔀 Merging without re-encoding...")

    # Create temporary file list for concat
    with open(TEMP_FILE, "w") as f:
        for video in VIDEOS_TO_MERGE:
            f.write(f"file '{os.path.abspath(video)}'\n")

    # Merge videos
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", TEMP_FILE,
        "-c", "copy",
        "-fflags", "+genpts",  # Optional, ensures timestamp continuity
        FINAL_VIDEO
    ], check=True)

    # Show final duration
    final_duration = get_video_duration(FINAL_VIDEO)
    print(f"\n🎉 Final duration: {final_duration:.2f} seconds")

    # Clean up
    if os.path.exists(TEMP_FILE):
        os.remove(TEMP_FILE)

if __name__ == "__main__":
    try:
        check_videos_exist()
        merge_videos_directly()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Try these solutions:")
        print("1. Ensure all videos have same codec, resolution, framerate, etc.")
        print("2. If not, convert them first using:")
        print("   ffmpeg -i input.mp4 -r 30 -c:v libx264 -crf 22 -c:a aac output_fixed.mp4")
