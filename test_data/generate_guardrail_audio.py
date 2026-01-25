# test_data/generate_guardrail_audio.py
from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Define input and output directories
samples_dir = Path("test_data/guardrail_tests")
audio_dir = Path("test_data/audio/guardrails")
audio_dir.mkdir(parents=True, exist_ok=True)

voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
current_voice = 0

# Generate audio for each transcript
files = list(samples_dir.glob("*.txt"))
print(f"Found {len(files)} transcript files")

for transcript_file in sorted(files):
    transcript = transcript_file.read_text()
    output_file = audio_dir / f"{transcript_file.stem}.mp3"
    
    if output_file.exists():
        print(f"⏭️  Skipping {output_file.name} (already exists)")
        continue
    
    voice = voices[current_voice % len(voices)]
    current_voice += 1
    
    print(f"🎙️  Generating {output_file.name} with voice '{voice}'...")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=transcript
        )
        response.stream_to_file(str(output_file))
        print(f"✓ Created {output_file}")
    except Exception as e:
        print(f"❌ Error generating audio for {transcript_file.name}: {e}")

print(f"\n✅ Done! Audio files saved to {audio_dir}")
