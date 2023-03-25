from pathlib import Path
import datetime as dt
import tempfile
import re
import subprocess
import os

school_opening_day = dt.datetime(2023, 2, 13)
# school_opening_day = dt.datetime(2022, 9, 5)
# school_opening_day = dt.datetime(2021, 9, 13)
target_dir = input("請貼上目標資料夾路徑 ")
recordings_dir = Path(target_dir)
course_name = recordings_dir.name
first_week_of_course = ""

first_run = True

def get_datetime(filename: str) -> dt.datetime:
    pattern = r'\d{8}_\d{6}'
    datetime_str = re.search(pattern, filename).group(0)
    return dt.datetime.strptime(datetime_str, "%Y%m%d_%H%M%S")

recordings = [ str(i) for i in recordings_dir.glob("*.mp4") ]
sorted_recordings = sorted(recordings, key = get_datetime)
sorted_recordings = [ Path(i) for i in sorted_recordings ]

group_recordings = {}

for recording in sorted_recordings:
    if (recording.is_file() and recording.suffix== '.mp4'):
        file = recording
        datetime_obj = get_datetime(file.stem)

        if (first_run):
            first_run = False
            course_weekday = datetime_obj.weekday()
            first_week_of_course = school_opening_day + dt.timedelta(days = course_weekday)
        
        diff = datetime_obj - first_week_of_course
        nth_week = (diff.days / 7) + 1
        if (nth_week.is_integer()):
            nth_week = int(nth_week)
        else:
            nth_week = round(nth_week, 1)
    
        if nth_week not in group_recordings:
            group_recordings[nth_week] = []
        group_recordings[nth_week].append(recording)

for group_id, values in group_recordings.items():
    print(f"週次 {group_id}")
    for value in values:
        print(value.stem)

response = input("上述的分類的週次都正確嗎? (yes/no) ")
if response in ("yes", "no"):
    if response == "yes":
        for group_id, values in group_recordings.items():
            
            output_file = course_name + "-W" + str(group_id) + ".mp4"
            output_file = Path(recordings_dir / output_file)
            if len(values) > 1:
                tmp = tempfile.NamedTemporaryFile(delete = False)
                
                for input_file in values:
                    line = f'file \'{input_file}\'\n'
                    tmp.write(line.encode())
                tmp.close()

                command = f'ffmpeg -f concat -safe 0 -i {tmp.name} -c copy {output_file}'

                process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if process.returncode == 0:
                    print(f'Successfully concatenated the videos and saved them as {output_file}.')
                else:
                    print(f'An error occurred during video concatenation. Error details: {process.stderr.decode("utf-8")}')

                os.unlink(tmp.name)
            else:
                print(f'Rename video filename as {output_file}.')
                values[0].rename(output_file)
    else:
        print("abort")
        
