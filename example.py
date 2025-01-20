import random
import string
import uuid
from hailuo_tts import HailuoTTS
# from env import API_KEY, GROUP_ID

# Get your API key from https://intl.minimaxi.com/user-center/basic-information/interface-key
API_KEY = "1234567890"
# Get your group ID from https://intl.minimaxi.com/user-center/basic-information
GROUP_ID = "1234567890"

def print_available_settings(tts: HailuoTTS):
    """Print all available settings and their constraints"""
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

    print("\nVoice Settings Constraints:")
    constraints = tts.get_voice_constraints()
    for param, values in constraints.items():
        print(f"- {param}: min={values['min']}, max={values['max']}, default={values['default']}")

def basic_example():
    """
    Basic example of text-to-speech usage
    """
    # Initialize with required parameters
    tts = HailuoTTS.create(
        api_key=API_KEY,  # Replace with your API key
        group_id=GROUP_ID  # Replace with your group ID
    )
    
    try:
        # Print all available settings
        print_available_settings(tts)

        tts.set_model("hd")
        
        # Basic usage with default settings (HD model)
        tts.text_to_speech(
            text="Hello! This is a basic test with default settings.",
            output_path="basic_test",
            format="mp3"
        )
        print("Audio saved to basic_test.mp3")
        
    except Exception as e:
        raise e
        print(f"Error: {str(e)}")

def custom_settings_example():
    """
    Example of using custom settings and updating them
    """
    # Create instance with turbo model
    tts = HailuoTTS.create(
        api_key=API_KEY,
        group_id=GROUP_ID,
        model="turbo"  # Use turbo model
    )
    
    try:
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
        print("Audio saved to custom_settings_test.mp3")
        
        # You can update individual settings at any time
        tts.update_model("hd")  # Switch to HD model
        tts.set_voice_params(speed=0.8)  # Only update speed
        tts.set_emotion(None)  # Remove emotion (not supported in HD model)
        
        # Try with new settings
        tts.text_to_speech(
            text="Now testing with HD model and slower speed.",
            output_path="hd_model_test"
        )
        print("Audio saved to hd_model_test.mp3")
        
    except Exception as e:
        print(f"Error: {str(e)}")

def voice_clone_example():
    """
    Example of voice cloning functionality
    WARNING: Using cloned voices costs $3 per confirmed voice!
    """
    tts = HailuoTTS.create(
        api_key=API_KEY,
        group_id=GROUP_ID
    )
    
    try:
        # Step 1: Upload voice file for cloning
        # Requirements:
        # - Format: MP3, M4A, WAV
        # - Duration: 10 seconds to 5 minutes
        # - Size: less than 20MB
        file_id = tts.upload_voice_file("test.mp3")
        print(f"File uploaded successfully, ID: {file_id}")
        
        # Step 2: Clone the voice and get demo audio
        # Note: Cloned voice is temporary and will be deleted after 168 hours (7 days)
        # unless used in T2A v2 API during this period
        voice_id = "MyVoice011"  # Must be at least 8 chars, contain letters and numbers, start with letter
        response, demo_path = tts.clone_voice(
            file_id=file_id,
            voice_id=voice_id,
            output_path=f"demo_{voice_id}",  # Demo will be saved as voice_demo.mp3
            noise_reduction=True,
            preview_text="Hello, this is a test message for the cloned voice.",
            preview_model="speech-01-turbo",  # Currently only turbo model is available for preview
            accuracy=0.8,
            volume_normalize=True
        )
        
        print("Voice cloned successfully")
        if demo_path:
            print(f"Demo audio downloaded and saved to: {demo_path}")
        else:
            print("No demo audio available or download failed")
            
        if 'demo_audio' in response:
            print(f"Demo audio URL: {response['demo_audio']}")
        
        # Step 3: Using cloned voice for text-to-speech
        # IMPORTANT: Once you use a cloned voice, it becomes available for all requests
        # Each confirmed voice will cost $3
        # Use with caution!
        
        # Uncomment the following code to use the cloned voice:
        """
        # Set the cloned voice ID
        tts.set_voice(voice_id)
        
        # Configure voice parameters if needed
        tts.set_voice_params(speed=1.2, volume=1.0, pitch=0)
        
        # Convert text to speech using the cloned voice
        text = "This is a test using my cloned voice. How does it sound?"
        tts.text_to_speech(
            text=text,
            output_path="cloned_voice_test",  # Will become cloned_voice_test.mp3
            format="mp3"
        )
        print("Audio saved to cloned_voice_test.mp3")
        """
            
    except Exception as e:
        print(f"Error: {str(e)}")

def test_voice_clone():
    tts = HailuoTTS.create(
        api_key=API_KEY,
        group_id=GROUP_ID
    )

    # We generate random uuid for file id
    file_id = str(uuid.uuid4())
    
    # Generatate random 8 chars
    voice_id = "T"+''.join(random.choices(string.ascii_letters + string.digits, k=7))

    # We upload the file
    file_id = tts.upload_voice_file("test.mp3")
    print(f"File uploaded successfully, ID: {file_id}")

    # We clone the voice
    text = "Hello, this is a test message for the cloned voice."
    response, demo_path = tts.clone_voice(file_id, voice_id, f"demo_{voice_id}", preview_text=text)

    print(response)
    print(demo_path)

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Basic usage")
    print("2. Custom settings")
    print("3. Voice cloning (costs $3 per confirmed voice!)")
    print("4. Test voice cloning")
    choice = input("Enter number (1-4): ")
    
    if choice == "1":
        basic_example()
    elif choice == "2":
        custom_settings_example()
    elif choice == "3":
        voice_clone_example()
    elif choice == "4":
        test_voice_clone()
    else:
        print("Invalid choice")