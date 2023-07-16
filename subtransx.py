import os
import numpy as np
import whisper
from datetime import timedelta

from pydub import AudioSegment
from pydub.utils import make_chunks

def process_subtitle_file(subtitle_file):
    with open(subtitle_file, 'r') as f:
        lines = f.read().strip().split('\n')

    subtitles = []
    current_subtitle = None
    for line in lines:
        line = line.strip()
        if line.isdigit():
            if current_subtitle:
                subtitles.append(current_subtitle)
            current_subtitle = {'index': int(line)}
        elif '-->' in line:
            start, end = line.split('-->')
            current_subtitle['start'] = parse_time(start.strip())
            current_subtitle['end'] = parse_time(end.strip())
        elif line != '':
            if 'text' not in current_subtitle:
                current_subtitle['text'] = []
            current_subtitle['text'].append(line)

    if current_subtitle:
        subtitles.append(current_subtitle)

    return subtitles

def parse_time(time_str):
    time_parts = time_str.split(':')
    hours = int(time_parts[0])
    minutes = int(time_parts[1])
    seconds, milliseconds = map(int, time_parts[2].split(','))

    return timedelta(hours=hours, minutes=minutes, seconds=seconds, milliseconds=milliseconds)


def extract_audio_segments(video_file, subtitles):
    audio = AudioSegment.from_file(video_file)
    audio_segments = []

    # Create the "input" folder if it doesn't exist
    os.makedirs("input", exist_ok=True)

    for i, subtitle in enumerate(subtitles):
        start = subtitle['start'].total_seconds() * 1000
        end = subtitle['end'].total_seconds() * 1000
        segment = audio[start:end]
        audio_segments.append(segment)

        # Output each segment to the "input" folder
        segment.export(f"input/segment_{i}.wav", format="wav")

    return audio_segments



def recognize_audio(audio_segments, subtitles):
    model = whisper.load_model("large-v2")  # Change this to your desired model
    recognized_texts = []

    for i, segment in enumerate(audio_segments):
        subtitle_text = subtitles[i]['text'] if i < len(subtitles) else 'Unknown'
        print(f"Processing subtitle line: {subtitle_text}")

        # Convert to 16kHz mono
        segment = segment.set_frame_rate(16000).set_channels(1)

        audio_np = np.array(segment.get_array_of_samples())
        audio_fp32 = audio_np.astype(np.float32) / 32767.0  # Convert to float32 in the range [-1, 1]
        transcribe = model.transcribe(audio=audio_fp32, language='fr')
        segments = transcribe['segments']

        text = ''
        for segment in segments:
            text += segment['text']

            # Print current transcribed text
            print(f"Current transcription: {segment['text']}")

        recognized_texts.append(text)

    return recognized_texts



def generate_updated_subtitle(subtitles, recognized_texts):
    updated_subtitles = []

    for i, subtitle in enumerate(subtitles):
        updated_subtitle = subtitle.copy()
        updated_subtitle['text'] = recognized_texts[i]
        updated_subtitles.append(updated_subtitle)

    return updated_subtitles


def generate_srt_content(subtitles, recognized_texts):
    lines = []

    for subtitle, recognized_text in zip(subtitles, recognized_texts):
        lines.append(str(subtitle['index']))

        start = subtitle['start']
        end = subtitle['end']

        start_str = format_timedelta(start)
        end_str = format_timedelta(end)

        lines.append(f"{start_str} --> {end_str}")

        lines.append(recognized_text)
        lines.append('')

    return '\n'.join(lines)




def format_timedelta(td):
    total_seconds = td.total_seconds()
    milliseconds = int(total_seconds * 1000) % 1000
    seconds = int(total_seconds) % 60
    minutes = int(total_seconds // 60) % 60
    hours = int(total_seconds // 3600)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"



# Specify the paths to your subtitle file and audio/video file
subtitle_file = 'your_subtitle.srt'
video_file = 'audio.wav'

# Process the subtitle file
subtitles = process_subtitle_file(subtitle_file)

# Extract audio segments from the video based on the time markers in the subtitle file
audio_segments = extract_audio_segments(video_file, subtitles)

# Recognize the text from the audio segments using the Whisper recognition engine
recognized_texts = recognize_audio(audio_segments, subtitles)

# Generate the updated subtitle content
 
updated_subtitles = generate_updated_subtitle(subtitles, recognized_texts)
updated_subtitle_content = generate_srt_content(updated_subtitles, recognized_texts)


# Write the updated subtitle content to a new file
updated_subtitle_file = 'updated_subtitle.srt'
with open(updated_subtitle_file, 'w', encoding='utf-8') as f:
    f.write(updated_subtitle_content)

print(f"Updated subtitle file '{updated_subtitle_file}' generated successfully!")
