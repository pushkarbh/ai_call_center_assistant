# Audio Test Data Creation Guide

This guide helps you create audio test files for validating the call center assistant's audio processing capabilities.

---

## Audio Format Requirements

**Supported Formats:**
- WAV (recommended for quality)
- MP3 (recommended for size)
- M4A

**Specifications:**
- Sample rate: 16kHz or 44.1kHz
- Channels: Mono (preferred) or Stereo
- Duration: 10 seconds to 60 minutes
- File size: < 25MB (OpenAI Whisper API limit)

---

## Method 1: Text-to-Speech (TTS) Tools

### ElevenLabs (Best Quality)
- URL: https://elevenlabs.io
- Free tier: 10,000 characters/month
- Steps:
  1. Sign up for free account
  2. Paste transcript text from `data/sample_transcripts/`
  3. Choose different voices for Agent and Customer
  4. Generate and download as MP3
  5. Save to `test_data/audio/`

### Google Cloud TTS (Good for Testing)
```bash
# Install Google Cloud TTS
pip install google-cloud-texttospeech

# Create test_data/generate_tts.py
```

### OpenAI TTS (Integrated)
```python
from openai import OpenAI
client = OpenAI()

response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",  # or: echo, fable, onyx, nova, shimmer
    input="Your transcript text here"
)
response.stream_to_file("test_data/audio/call.mp3")
```

---

## Method 2: Record Your Own

### Using QuickTime (Mac)
1. Open QuickTime Player
2. File → New Audio Recording
3. Click red record button
4. Read transcript (alternate voices for agent/customer)
5. File → Export As → Audio Only
6. Save as M4A or MP3

### Using Audacity (Windows/Mac/Linux)
1. Download: https://www.audacityteam.org
2. Click red record button
3. Read transcript
4. File → Export → Export as MP3/WAV
5. Save to `test_data/audio/`

---

## Method 3: Free Audio Samples

### BBC Sound Effects (Royalty-Free)
- URL: https://sound-effects.bbcrewind.co.uk
- Search for: "office", "telephone", "conversation"
- Download WAV files

### Freesound (Creative Commons)
- URL: https://freesound.org
- Search for: "phone call", "customer service"
- Filter by license: CC0 or CC-BY
- Download and save to `test_data/audio/`

---

## Test Cases to Create

### Valid Call Audio (10 files recommended)

1. **billing_inquiry.mp3** (from existing transcript)
   - Mood: Polite, professional
   - Topic: Billing discrepancy
   - Duration: ~2 minutes

2. **tech_support_frustrated.mp3**
   - Mood: Frustrated but resolved
   - Topic: Internet outage
   - Duration: ~3 minutes

3. **sales_upgrade.mp3**
   - Mood: Enthusiastic, positive
   - Topic: Plan upgrade
   - Duration: ~4 minutes

4. **complaint_angry.mp3**
   - Mood: Very angry, then satisfied
   - Topic: Double charge
   - Duration: ~3 minutes

5. **quick_password_reset.mp3**
   - Mood: Neutral, efficient
   - Topic: Password reset
   - Duration: ~1 minute (edge case: very short)

6. **noisy_background.mp3**
   - Mood: Professional despite noise
   - Topic: Order status
   - Add background noise/static to test robustness

7. **heavy_accent.mp3**
   - Use non-native speaker voice to test Whisper
   - Topic: Account help

8. **multiple_issues.mp3**
   - Customer has 3 different problems
   - Tests complex summarization

9. **escalation_to_supervisor.mp3**
   - Call gets escalated mid-conversation
   - Tests "escalated" resolution status

10. **positive_feedback.mp3**
    - Customer calling to praise service
    - Tests positive sentiment

### Invalid Audio (Edge Cases - 6 files)

1. **podcast_monologue.mp3**
   - Single person talking about tech
   - Should be flagged: Not a call (single speaker)

2. **music_instrumental.mp3**
   - Background music or hold music
   - Should be flagged: No speech detected

3. **song_with_lyrics.mp3**
   - Song with singing
   - Should be flagged: Not a conversation

4. **sports_commentary.mp3**
   - Sports announcer/commentary
   - Should be flagged: Not customer service

5. **blank_audio.mp3**
   - Silent audio or white noise
   - Should be flagged: No content

6. **multiple_people_meeting.mp3**
   - 4-5 people in a meeting (not 2-person call)
   - Should be flagged: Wrong format

---

## Quick TTS Script for OpenAI

Create `test_data/generate_audio_samples.py`:

```python
from openai import OpenAI
from pathlib import Path
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Read transcripts and generate audio
samples_dir = Path("data/sample_transcripts")
audio_dir = Path("test_data/audio")
audio_dir.mkdir(exist_ok=True)

voices = {
    "agent": "alloy",    # Professional female voice
    "customer": "onyx"   # Male voice
}

for transcript_file in samples_dir.glob("*.txt"):
    transcript = transcript_file.read_text()
    output_file = audio_dir / f"{transcript_file.stem}.mp3"
    
    print(f"Generating {output_file.name}...")
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",  # Mix of both voices - simplified for now
        input=transcript
    )
    
    response.stream_to_file(str(output_file))
    print(f"✓ Created {output_file}")

print(f"\nGenerated {len(list(audio_dir.glob('*.mp3')))} audio files")
```

Run with:
```bash
python test_data/generate_audio_samples.py
```

---

## Creating Invalid Test Cases

### Blank Audio (using ffmpeg)
```bash
# Install ffmpeg: brew install ffmpeg (Mac) or apt-get install ffmpeg (Linux)

# Create 30 seconds of silence
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 30 -acodec mp3 test_data/audio/blank_audio.mp3
```

### Instrumental Music
- Download from: https://www.bensound.com (royalty-free)
- Or use: https://incompetech.com (Creative Commons)

### Podcast/Monologue
- Record yourself talking about any topic for 2 minutes
- Or download from: https://archive.org/details/podcasts

---

## Directory Structure

```
test_data/
├── audio/                          # Audio files
│   ├── valid/                      # Valid call recordings
│   │   ├── billing_inquiry.mp3
│   │   ├── tech_support.mp3
│   │   └── ...
│   └── invalid/                    # Invalid audio for testing
│       ├── podcast_monologue.mp3
│       ├── music_instrumental.mp3
│       └── ...
├── transcripts/                    # Text transcripts (already created)
└── generate_audio_samples.py       # TTS generation script
```

---

## Testing Checklist

- [ ] At least 5 valid call audio files (different sentiments)
- [ ] At least 3 invalid audio files (edge cases)
- [ ] File sizes under 25MB each
- [ ] Mix of MP3 and WAV formats
- [ ] Various durations (1 min to 10 min)
- [ ] Clear audio quality
- [ ] Background noise variation (some clean, some noisy)

---

## Cost Estimates

| Method | Cost | Quality | Speed |
|--------|------|---------|-------|
| OpenAI TTS | ~$0.015/min | Good | Fast |
| ElevenLabs Free | Free (10k chars) | Excellent | Medium |
| Record Yourself | Free | Variable | Slow |
| Free Samples | Free | Variable | Fast |

**Recommendation:** Start with OpenAI TTS for quick testing, then add real recordings for production validation.

---

## Next Steps

1. Run the TTS generation script above
2. Test audio files work with Whisper API
3. Validate guardrails catch invalid audio
4. Create evaluation dataset
