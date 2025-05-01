import os
import random
import subprocess

INPUT_VIDEO = "input.mp4"
OUTPUT_VIDEO = "trailer.mp4"
DURATION_PER_CLIP = 3  # seconds
TOTAL_DURATION = 35    # seconds
NUM_CLIPS = TOTAL_DURATION // DURATION_PER_CLIP

def extract_random_clips():
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

    random_starts = random.sample(range(video_duration - DURATION_PER_CLIP), NUM_CLIPS)
    return random_starts

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

def create_image_intro():
    image_files = ["trailer1.jpeg", "trailer2.jpeg", "trailer3.jpeg"]
    with open("image_list.txt", "w") as f:
        for image in image_files:
            image_clip = f"{image}.mp4"
            subprocess.run([
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", image,
                "-t", "3",
                "-vf", "scale=1280:720",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                image_clip
            ], check=True)
            f.write(f"file '{image_clip}'\n")
            f.write("duration 2\n")
            print(f"🖼️ Image clip created: {image_clip}")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", "image_list.txt",
        "-c", "copy", "intro.mp4"
    ], check=True)
    print("🎬 Intro video created: intro.mp4")

def has_audio_stream(file_path):
    result = subprocess.run(
        ["ffprobe", "-i", file_path, "-show_streams", "-select_streams", "a", "-loglevel", "error"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return bool(result.stdout.strip())

def create_video():
    print("🎞️ Generating trailer...")

    temp_clips_video = "temp1_video.mp4"
    full_trailer_video = "temp2_full_video.mp4"

    # Create video from clips
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "clip_list.txt",
        "-vsync", "vfr", "-pix_fmt", "yuv420p", temp_clips_video
    ], check=True)
    print(f"✅ Clips video created: {temp_clips_video}")

    # Combine intro + clips
    with open("final_list.txt", "w") as f:
        f.write("file 'intro.mp4'\n")
        f.write(f"file '{temp_clips_video}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "final_list.txt",
        "-c", "copy", full_trailer_video
    ], check=True)
    print(f"✅ Full trailer created (intro + clips): {full_trailer_video}")

    # Add background music
    if has_audio_stream(full_trailer_video):
        print("🔈 Original audio found. Mixing with background music...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", full_trailer_video,
            "-i", "music.mp3",
            "-filter_complex",
            "[0:a]volume=0.08[a1];[1:a]volume=1.0[a2];[a1][a2]amix=inputs=2:duration=shortest[aout]",
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            OUTPUT_VIDEO
        ], check=True)
    else:
        print("🎵 No original audio found. Adding only background music...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", full_trailer_video,
            "-i", "music.mp3",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            OUTPUT_VIDEO
        ], check=True)

    print(f"✅ Final trailer with music created: {OUTPUT_VIDEO}")

    # Cleanup intermediate files
    for f in ["intro.mp4", temp_clips_video, full_trailer_video, "final_list.txt"]:
        if os.path.exists(f):
            os.remove(f)

def main():
    try:
        create_image_intro()
        random_starts = extract_random_clips()
        create_clip_list(random_starts)
        create_video()
    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        # Clean up clip files
        for start_time in range(0, 10000):  # big range to cover all generated clips
            clip_filename = f"clip_{start_time}.mp4"
            if os.path.exists(clip_filename):
                os.remove(clip_filename)
        # Clean up image clips
        for i in range(1, 4):
            img_clip = f"trailer{i}.jpeg.mp4"
            if os.path.exists(img_clip):
                os.remove(img_clip)
        # Clean up lists
        for list_file in ["clip_list.txt", "image_list.txt"]:
            if os.path.exists(list_file):
                os.remove(list_file)

if __name__ == "__main__":
    main()
