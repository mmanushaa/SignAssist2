import os




VIDEOS_FOLDER = r"vedios - Copy - Copy"
all_files = os.listdir(VIDEOS_FOLDER)
mp4_files = [f for f in all_files if f.endswith('.mp4')]

print("Total files:", len(all_files))
print("MP4 files:", len(mp4_files))
print("Filenames found:")
for f in mp4_files:
    print("-", f)

