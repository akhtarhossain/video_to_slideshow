import os
import random
import subprocess

INPUT_VIDEO = "input.mp4"
OUTPUT_VIDEO = "trailer.mp4"
DURATION_PER_CLIP = 3  # seconds
TOTAL_DURATION = 35    # seconds
NUM_CLIPS = TOTAL_DURATION // DURATION_PER_CLIP
MUSIC_START_TIME = 8   # start music from 8 seconds
SLOW_FACTOR = 1.2      # 20% slower (35s -> 42s approx)

def extract_random_clips():
    # Get video duration
    result = subprocess.run(
        ["ffmpeg", "-i", INPUT_VIDEO],
        stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )
    output = result.stderr.decode("utf-8")
    duration_line = [line for line in output.split("\n") if "Duration" in line]

    if not duration_line:
        raise Exception("❌ Unable to retrieve video duration.")

    duration_str = duration_line[0].split(",")[0].split("Duration: ")[1].strip()
    h, m, s = map(float, duration_str.split(":"))
    video_duration = int(h * 3600 + m * 60 + s)

    print(f"🎥 Video Duration: {video_duration} seconds")

    # Calculate maximum possible unique clips
    max_possible_clips = (video_duration - DURATION_PER_CLIP) // DURATION_PER_CLIP
    if max_possible_clips < NUM_CLIPS:
        raise Exception(f"❌ Not enough video content. Need at least {NUM_CLIPS * DURATION_PER_CLIP} seconds of unique content.")

    # Generate non-overlapping random start times (in random order)
    possible_starts = list(range(0, video_duration - DURATION_PER_CLIP, DURATION_PER_CLIP))
    random_starts = random.sample(possible_starts, NUM_CLIPS)  # No sorting here

    return random_starts  # Returns in random order

def create_clip_list(random_starts):
    with open("clip_list.txt", "w") as f:
        for start_time in random_starts:
            clip_filename = f"clip_{start_time}.mp4"
            f.write(f"file '{clip_filename}'\n")
            f.write(f"duration {DURATION_PER_CLIP}\n")

            subprocess.run([
                "ffmpeg", "-y",
                "-ss", str(start_time),
                "-t", str(DURATION_PER_CLIP),
                "-i", INPUT_VIDEO,
                "-c:v", "libx264",
                "-c:a", "aac",
                clip_filename
            ], check=True)
            print(f"✅ Clip created: {clip_filename} ({start_time}-{start_time + DURATION_PER_CLIP}s)")

def has_audio_stream(file_path):
    result = subprocess.run(
        ["ffprobe", "-i", file_path, "-show_streams", "-select_streams", "a", "-loglevel", "error"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return bool(result.stdout.strip())

def create_video():
    print("🎞️ Generating trailer...")

    # Step 1: Create video from clips
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clip_list.txt",
        "-vsync", "vfr", "-pix_fmt", "yuv420p", "temp_video.mp4"
    ], check=True)
    print("✅ Random clips video created: temp_video.mp4")

    # Step 2: Create trimmed music
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", str(MUSIC_START_TIME),
        "-i", "music.mp3",
        "-c", "copy", "trimmed_music.mp3"
    ], check=True)
    print("🎵 Trimmed music created (starting from 8 seconds)")

    # Step 3: Add background music
    audio_mixed_output = "audio_video_mix.mp4"
    if has_audio_stream("temp_video.mp4"):
        print("🔈 Original audio found. Mixing with background music...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", "temp_video.mp4",
            "-i", "trimmed_music.mp3",
            "-filter_complex",
            "[0:a]volume=0.02[a1];[1:a]volume=1.0[a2];[a1][a2]amix=inputs=2:duration=shortest[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            audio_mixed_output
        ], check=True)
    else:
        print("🎵 No original audio found. Adding only background music...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", "temp_video.mp4",
            "-i", "trimmed_music.mp3",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            audio_mixed_output
        ], check=True)

    print("🪞 Applying mirror and slowing down video...")

    # Step 4: Apply mirror effect and slow down video (setpts), output final trailer
    subprocess.run([
        "ffmpeg", "-y",
        "-i", audio_mixed_output,
        "-vf", f"hflip,setpts={SLOW_FACTOR}*PTS",
        "-c:a", "copy",
        OUTPUT_VIDEO
    ], check=True)

    print(f"✅ Final mirrored & slowed trailer created: {OUTPUT_VIDEO}")

    # Step 5: Cleanup intermediate files
    for f in ["temp_video.mp4", "trimmed_music.mp3", audio_mixed_output]:
        if os.path.exists(f):
            os.remove(f)

def main():
    try:
        random_starts = extract_random_clips()
        create_clip_list(random_starts)
        create_video()
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        # Clean up clip files
        for start_time in range(0, 10000):
            clip_filename = f"clip_{start_time}.mp4"
            if os.path.exists(clip_filename):
                os.remove(clip_filename)
        # Clean up lists
        if os.path.exists("clip_list.txt"):
            os.remove("clip_list.txt")

if __name__ == "__main__":
    main()
