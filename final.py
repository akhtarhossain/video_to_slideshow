import os
import subprocess

# Input videos
VIDEOS_TO_MERGE = ["new.mp4", "last.mp4"]
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

def normalize_video(input_file, output_file):
    """Re-encode video and audio with synced durations to avoid pitch issues"""
    print(f"🔄 Re-encoding {input_file} with synced audio/video...")
    subprocess.run([
        "ffmpeg", "-y", "-i", input_file,
        "-r", "30",                      # Normalize frame rate
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",                  # ✅ Force 48kHz for MP4 standard
        "-ac", "2",                      # ✅ Stereo
        "-movflags", "+faststart",
        "-pix_fmt", "yuv420p",
        output_file
    ], check=True)

def merge_videos():
    print("🔀 Merging with accurate durations...")
    
    # Normalize all videos first
    temp_files = []
    try:
        for i, video in enumerate(VIDEOS_TO_MERGE):
            temp_file = f"normalized_{i}.mp4"
            normalize_video(video, temp_file)
            temp_files.append(temp_file)
        
        # Verify normalized durations
        print("\n✅ Normalized Video Durations:")
        total_duration = 0
        for temp_file in temp_files:
            duration = get_video_duration(temp_file)
            total_duration += duration
            mins, secs = divmod(duration, 60)
            hours, mins = divmod(mins, 60)
            print(f"  {temp_file}: {int(hours):02d}:{int(mins):02d}:{int(secs):02d}")
        
        # Create merge list
        with open(TEMP_FILE, "w") as f:
            for temp_file in temp_files:
                f.write(f"file '{temp_file}'\n")
        
        # Merge with accurate concatenation
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", TEMP_FILE,
            "-c", "copy",               # Stream copy for faster merging
            "-fflags", "+genpts",       # Ensure proper timestamps
            FINAL_VIDEO
        ], check=True)
        
        # Verify final duration
        final_duration = get_video_duration(FINAL_VIDEO)
        print(f"\n🎉 Final duration: {final_duration:.2f}s (Expected: {total_duration:.2f}s)")
        print(f"   Difference: {final_duration-total_duration:.2f}s")
        
    finally:
        # Cleanup
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)

if __name__ == "__main__":
    try:
        check_videos_exist()
        merge_videos()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Try these solutions:")
        print("1. Check each video plays properly in VLC/MPV")
        print("2. Convert problematic videos separately first:")
        print("   ffmpeg -i problem.mp4 -r 30 -c:v libx264 -crf 22 -c:a aac fixed.mp4")