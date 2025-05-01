import subprocess

input_file = "final_output.mp4"  # apni original video ka naam yahan likhein
output_file = "output_cut.mp4"  # final video ka naam

# 2 hours 21 minutes = 02:21:00
cut_duration = "02:10:00"

# ffmpeg command to trim the video
command = [
    "ffmpeg",
    "-i", input_file,
    "-t", cut_duration,  # -t means duration
    "-c", "copy",        # copy without re-encoding
    output_file
]

# Run the command
subprocess.run(command)

print("Done! Last 32 minutes cut ho chuki hain.")
