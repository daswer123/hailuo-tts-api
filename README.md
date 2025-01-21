# Hailuo TTS API Wrapper

A comprehensive Python wrapper for the Hailuo Text-to-Speech API with voice cloning support. This wrapper provides easy access to all API features including text-to-speech synthesis and voice cloning capabilities.

## 🎯 Try Demo Without Installation

Want to test the capabilities before installing? Try our interactive demo:

**[➡️ Try Hailuo TTS Demo on Hugging Face](https://huggingface.co/spaces/daswer123/Hailio-TTS-API)**

Note: You'll need your own API credentials to use the demo. Don't worry, getting them is easy - just follow the instructions below!

## Getting Started

### Get Your API Credentials

1. Get your API key from [User Center - Interface Key](https://intl.minimaxi.com/user-center/basic-information/interface-key)
2. Get your Group ID from [User Center - Basic Information](https://intl.minimaxi.com/user-center/basic-information)

### Installation

```bash
pip install hailuo-tts-api
```

## Basic Usage

```python
from hailuo_tts import HailuoTTS

# Initialize with required parameters
tts = HailuoTTS.create(
    api_key="your_api_key",
    group_id="your_group_id"
)

# Basic usage with default settings (HD model)
tts.text_to_speech(
    text="Hello! This is a basic test with default settings.",
    output_path="basic_test",
    format="mp3"
)
```

## Custom Settings Example

```python
# Create instance with turbo model
tts = HailuoTTS.create(
    api_key="your_api_key",
    group_id="your_group_id",
    model="turbo"  # Use turbo model
)

# Set voice and its parameters
tts.set_voice("Calm_Woman")
tts.set_voice_params(
    speed=1.2,    # Range: 0.5 to 2.0
    volume=1.5,   # Range: 0 to 10
    pitch=2       # Range: -12 to 12
)

# Set emotion (only for turbo model)
tts.set_emotion("happy")  # One of: happy, sad, angry, fearful, disgusted, surprised, neutral

# Set language boost
tts.set_language_boost("Russian")

# Update audio settings
tts.update_audio_settings(
    sample_rate=32000,  # One of: 8000, 16000, 22050, 24000, 32000
    bitrate=128000,     # One of: 32000, 64000, 128000
    format="mp3",       # One of: mp3, pcm, flac
    channel=1           # 1: mono, 2: stereo
)

# Convert text to speech with current settings
tts.text_to_speech(
    text="Hello! This is a test with custom voice settings.",
    output_path="custom_settings_test"
)
```

## Voice Cloning

⚠️ **IMPORTANT: Using cloned voices costs $3 per confirmed voice!**

```python
# Initialize
tts = HailuoTTS.create(api_key="your_api_key", group_id="your_group_id")

# Step 1: Upload voice file for cloning
# Requirements:
# - Format: MP3, M4A, WAV
# - Duration: 10 seconds to 5 minutes
# - Size: less than 20MB
file_id = tts.upload_voice_file("sample.mp3")

# Step 2: Clone the voice and get demo audio
# Note: Cloned voice is temporary and will be deleted after 168 hours (7 days)
# unless used in T2A v2 API during this period
voice_id = "MyVoice123"  # Must be at least 8 chars, contain letters and numbers, start with letter
response, demo_path = tts.clone_voice(
    file_id=file_id,
    voice_id=voice_id,
    output_path="demo_voice",
    noise_reduction=True,
    preview_text="Hello, this is a test message for the cloned voice.",
    preview_model="speech-01-turbo",  # Currently only turbo model is available for preview
    accuracy=0.8,
    volume_normalize=True
)

# Step 3: Using cloned voice for text-to-speech
# IMPORTANT: Once you use a cloned voice, it becomes available for all requests
# Each confirmed voice will cost $3
tts.set_voice(voice_id)
tts.text_to_speech(
    text="This is a test using my cloned voice. How does it sound?",
    output_path="cloned_voice_test"
)
```

## Available Settings

### Models

1. **HD Model** (`"hd"`)
   - Rich voices
   - Authentic language support
   - High-quality output

2. **Turbo Model** (`"turbo"`)
   - Latest model
   - Excellent performance
   - Low latency
   - Emotion support

### Voice Parameters

- **Speed**: 0.5 to 2.0 (default: 1.0)
- **Volume**: 0 to 10 (default: 1.0)
- **Pitch**: -12 to 12 (default: 0)

### Audio Settings

- **Sample Rates**: 8000, 16000, 22050, 24000, 32000 Hz
- **Bitrates**: 32000, 64000, 128000 bps
- **Formats**: mp3, pcm, flac
- **Channels**: mono (1), stereo (2)

### Available Voices

- Wise_Woman
- Friendly_Person
- Inspirational_girl
- Deep_Voice_Man
- Calm_Woman
- Casual_Guy
- Lively_Girl
- Patient_Man
- Young_Knight
- Determined_Man
- Lovely_Girl
- Decent_Boy
- Imposing_Manner
- Elegant_Man
- Abbess
- Sweet_Girl_2
- Exuberant_Girl

### Emotions (Turbo model only)

- happy
- sad
- angry
- fearful
- disgusted
- surprised
- neutral

### Supported Languages

- Spanish
- French
- Portuguese
- Korean
- Indonesian
- German
- Japanese
- Italian
- Chinese
- Chinese,Yue
- auto (automatic detection)

## Voice Cloning Details

### File Requirements

- **Format**: MP3, M4A, WAV
- **Duration**: 10 seconds to 5 minutes
- **Size**: Less than 20MB

### Important Notes

1. Voice preview is synthesized using the turbo model
2. No charge for cloning itself, only for synthesis
3. First use of a cloned voice in TTS incurs a $3 fee
4. Cloned voices are temporary (168 hours/7 days) unless used in TTS
5. Voice ID must be at least 8 characters, contain letters and numbers, and start with a letter

## Checking Available Settings

```python
# Print all available settings and their constraints
print("\nAvailable Models:")
for model, desc in tts.get_available_models().items():
    print(f"- {model}: {desc}")

print("\nAvailable Voices:")
for voice in tts.get_available_voices():
    print(f"- {voice}")

print("\nAvailable Emotions (only for turbo model):")
for emotion in tts.get_available_emotions():
    print(f"- {emotion}")

print("\nSupported Languages:")
for lang in tts.get_available_languages():
    print(f"- {lang}")

print("\nAudio Settings Constraints:")
constraints = tts.get_audio_constraints()
print(f"- Sample Rates: {constraints['sample_rate']}")
print(f"- Bitrates: {constraints['bitrate']}")
print(f"- Formats: {constraints['format']}")
print(f"- Channels: {constraints['channel']} (1: mono, 2: stereo)")
```

## Official Documentation

For more details, see the [official Hailuo TTS documentation](https://intl.minimaxi.com/document/T2A%20V2?key=66719005a427f0c8a5701643)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
