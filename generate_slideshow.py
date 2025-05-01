import os
import random
import subprocess
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, CompositeVideoClip
from moviepy.video.fx.all import crop

IMAGES_DIR = "clear_scenes"
ALL_IMAGES_DIR = "all"
INPUT_VIDEO = "input.webm"
OUTPUT_VIDEO = "slideshow_1hour.mp4"
TOTAL_DURATION = 1500  # seconds (25 minutes for demonstration)
INITIAL_VIDEO_DURATION = 35
INITIAL_CLIP_DURATION = 3
ALL_IMAGES_DURATION = 5
LONG_DURATION_IMAGE = 40
SHORT_DURATION_IMAGE = 10
GIF_URL = "https://www.behance.net/gallery/68481015/GIF-Loader/modules/400188135"  # For demonstration; you'll need to download it

def get_random_cuts_from_video(video_path, total_duration, clip_duration):
    try:
        video = VideoFileClip(video_path)
        video_duration = video.duration
        num_clips = total_duration // clip_duration
        clips = []
        for _ in range(num_clips):
            start_time = random.uniform(0, max(0, video_duration - clip_duration))
            end_time = start_time + clip_duration
            clip = video.subclip(start_time, end_time)
            clips.append(clip)
        return clips
    except Exception as e:
        print(f"⚠️ Error processing video: {e}")
        return []

def get_image_clips(image_dir, duration):
    image_files = sorted(os.listdir(image_dir))
    if not image_files:
        print(f"⚠️ No images found in {image_dir}.")
        return []
    clips = [ImageClip(os.path.join(image_dir, img), duration=duration) for img in image_files]
    return clips

def get_random_image_clips(image_dir, num_clips, duration):
    image_files = os.listdir(image_dir)
    if not image_files:
        print(f"⚠️ No images found in {image_dir}.")
        return []
    selected_images = random.choices(image_files, k=num_clips)
    clips = [ImageClip(os.path.join(image_dir, img), duration=duration) for img in selected_images]
    return clips

def download_gif(url, filename="loading.gif"):
    try:
        subprocess.run(["wget", "-O", filename, url], check=True)
        return filename
    except Exception as e:
        print(f"⚠️ Error downloading GIF: {e}")
        return None

def main():
    final_clips = []

    # Part 1: Random cuts from input video
    print("🎬 Creating initial video clips...")
    video_clips = get_random_cuts_from_video(INPUT_VIDEO, INITIAL_VIDEO_DURATION, INITIAL_CLIP_DURATION)
    final_clips.extend(video_clips)

    # Part 2: Images from 'all' folder
    print("🖼️ Adding images from 'all' folder...")
    all_image_clips = get_image_clips(ALL_IMAGES_DIR, ALL_IMAGES_DURATION)
    final_clips.extend(all_image_clips)

    # Part 3: Images from 'clear_scenes' with long duration and GIF overlay
    print("🏞️ Adding images from 'clear_scenes' with long duration and GIF...")
    clear_scenes_images = os.listdir(IMAGES_DIR)
    if clear_scenes_images:
        gif_file = download_gif(GIF_URL)
        if gif_file:
            gif_clip = VideoFileClip(gif_file).loop(duration=TOTAL_DURATION)
            gif_clip_resized = gif_clip.resize(width=200) # Adjust size as needed
            gif_clip_positioned = gif_clip_resized.set_position("center")

        current_duration = sum(clip.duration for clip in final_clips)
        while current_duration < 1500: # Aiming for around 25 minutes for this phase
            img = random.choice(clear_scenes_images)
            img_clip = ImageClip(os.path.join(IMAGES_DIR, img), duration=LONG_DURATION_IMAGE)
            final_clips.append(img_clip)
            current_duration += LONG_DURATION_IMAGE
            if gif_file and current_duration < 1500:
                final_clips[-1] = CompositeVideoClip([final_clips[-1], gif_clip_positioned.set_duration(LONG_DURATION_IMAGE)])

    # Part 4: Images from 'clear_scenes' with short duration until total duration
    print("🏞️ Adding remaining images from 'clear_scenes' with short duration...")
    remaining_duration = TOTAL_DURATION - sum(clip.duration for clip in final_clips)
    if remaining_duration > 0 and clear_scenes_images:
        num_remaining_clips = remaining_duration // SHORT_DURATION_IMAGE + 1
        short_duration_clips = get_random_image_clips(IMAGES_DIR, int(num_remaining_clips), SHORT_DURATION_IMAGE)
        final_clips.extend(short_duration_clips)

    # Final video creation
    if final_clips:
        print("🎬 Finalizing video...")
        final_video = concatenate_videoclips(final_clips, method="compose")
        final_video.write_videofile(OUTPUT_VIDEO, fps=24, codec="libx264", audio_codec="aac")
        print(f"✅ Slideshow video created: {OUTPUT_VIDEO}")
    else:
        print("⚠️ No video clips to create.")

if __name__ == "__main__":
    main()