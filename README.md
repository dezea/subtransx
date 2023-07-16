# subtransx
SubTransX is a Python script that allows you to use time codes from an existing subtitle to transcribe and create new subtitles for audio in other languages than the original.
It uses the Whisper speech recognition engine to convert audio segments into text and provides an automated process for updating subtitle files with the transcribed text.

Requirements:
Pydub, numpy, whisper, torch, torchaudio

Usage:
Place in the same folder as the script:
- your_subtitle.srt // an existing subtitle in any language, but correctly synchronized with the audio, from which the script will get the time codes
- audio.wav // the audio track in the new language you want the output subtitle to be in (The script might already work with video though or can be easily updated to do so anyway if you need that)
- change the language code to the one of your audio file in the line: "transcribe = model.transcribe(audio=audio_fp32, language='fr')"
If all goes well, you will get an updated_subtitle.srt in the same folder which contains the new subtitle for the language of your audio file, using the time codes in the input srt file.

I might do a command line for it and add some pre-processing on the srt to make it work better if there's interest (eg, merging of continuation line will help a ton and doing that first is recommended)



