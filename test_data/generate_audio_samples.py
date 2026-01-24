from openai import OpenAI
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create audio directory
audio_dir = Path("test_data/audio/valid")
audio_dir.mkdir(parents=True, exist_ok=True)

# Read transcripts from sample_transcripts
samples_dir = Path("data/sample_transcripts")

if not samples_dir.exists():
    print(f"Error: {samples_dir} not found")
    exit(1)

voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
current_voice = 0

for transcript_file in samples_dir.glob("*.txt"):
    transcript = transcript_file.read_text()
    output_file = audio_dir / f"{transcript_file.stem}.mp3"
    
    # Use different voice for each file
    voice = voices[current_voice % len(voices)]
    current_voice += 1
    
    print(f"Generating {output_file.name} with voice '{voice}'...")
    
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=transcript
        )
        
        response.stream_to_file(str(output_file))
        print(f"✓ Created {output_file}")
    except Exception as e:
        print(f"✗ Failed to create {output_file}: {e}")

print(f"\n✓ Generated {len(list(audio_dir.glob('*.mp3')))} audio files in {audio_dir}")
print(f"\nNext: Create invalid test cases manually (see AUDIO_GENERATION_GUIDE.md)")
