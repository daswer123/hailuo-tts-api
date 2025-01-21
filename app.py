import random
import string
import gradio as gr
from hailuo_tts import HailuoTTS
import os

# Global variable to store TTS instance
tts_instance = None

def authorize(api_key, group_id):
    """Authorization function and TTS instance creation"""
    global tts_instance
    try:
        tts_instance = HailuoTTS.create(api_key=api_key, group_id=group_id)
        return gr.update(visible=True), gr.update(visible=False)
    except Exception as e:
        return gr.update(visible=False), gr.update(visible=True, value=f"Authorization error: {str(e)}")

def on_model_change(model):
    """Interface update when model changes"""
    show_emotions = model == "turbo"
    return gr.update(visible=show_emotions)

def text_to_speech(text, model, voice, speed, volume, pitch, emotion, language,
                  sample_rate, bitrate, audio_format, channel):
    """Text to speech generation function"""
    global tts_instance
    try:
        # Update settings
        tts_instance.set_model(model)
        tts_instance.set_voice(voice)
        tts_instance.set_voice_params(speed=float(speed), volume=float(volume), pitch=int(pitch))
        
        if model == "turbo" and emotion:
            tts_instance.set_emotion(emotion)
        
        if language != "auto":
            tts_instance.set_language_boost(language)
            
        # Update audio settings
        tts_instance.update_audio_settings(
            sample_rate=int(sample_rate),
            bitrate=int(bitrate),
            format=audio_format,
            channel=int(channel)
        )
            
        # Generate speech
        output_path = f"output.{audio_format}"
        tts_instance.text_to_speech(text, output_path)
        
        return output_path, "Audio generated successfully!"
    except Exception as e:
        return None, f"Error: {str(e)}"

def generate_random_voice_id():
    return "random_" + ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def show_voice_id_input(use_custom_voice_id):
    return gr.update(visible=not use_custom_voice_id)

def clone_voice(audio_file, voice_id, noise_reduction, preview_text, accuracy, volume_normalize,use_custom_voice_id):
    """Voice cloning function"""
    global tts_instance
    try:
        # Upload file
        file_id = tts_instance.upload_voice_file(audio_file.name)

        voice_id = voice_id if not use_custom_voice_id else generate_random_voice_id()
        print(voice_id)
        
        # Clone voice
        response, demo_path = tts_instance.clone_voice(
            file_id=file_id,
            voice_id=voice_id,
            noise_reduction=noise_reduction,
            preview_text=preview_text,
            accuracy=float(accuracy),
            volume_normalize=volume_normalize
        )
        
        return demo_path, f"Voice cloned successfully! Voice ID: {voice_id}"
    except Exception as e:
        return None, f"Error: {str(e)}"

# Create interface
with gr.Blocks() as app:
    # Authorization screen
    with gr.Accordion("Authorization", open=True):
        gr.Markdown("""
# Hailio TTS - Text-to-Speech Service

## Important Links
1. List of supported languages: https://www.hailuo.ai/audio
2. Get your API credentials:
   - Group ID and API Key can be found at:
   - https://intl.minimaxi.com/user-center/basic-information
   - https://intl.minimaxi.com/user-center/basic-information/interface-key

## Pricing
- Turbo Model: $50 per 1M characters
- HD Model: $30 per 1M characters
- Voice Cloning:
  - Verified voice clone: $3 per voice
  - Unverified voice clone: Free
""")
        with gr.Row(visible=True) as auth_row:
            with gr.Column():
                api_key = gr.Textbox(label="API Key",type="password", placeholder="Enter your API key")
                group_id = gr.Textbox(label="Group ID",type="password", placeholder="Enter your Group ID")
                auth_btn = gr.Button("Authorize")
                auth_error = gr.Textbox(label="Status", interactive=False)
    
    # Main interface (initially hidden)
    with gr.Tabs(visible=False) as tabs:
        # TTS tab

        with gr.Tab("Text to Speech"):
            with gr.Row():
                with gr.Column():
                    # Main parameters
                    text_input = gr.Textbox(label="Text", placeholder="Enter text for speech", lines=5)
                    model = gr.Dropdown(choices=["turbo", "hd"], value="hd",info="Emotions work only with turbo model", label="Model")
                    voice = gr.Dropdown(choices=HailuoTTS.VOICES, allow_custom_value=True, value="Friendly_Person", label="VoiceId", info="You can set a custom value here, for example you can specify the voice ID that you cloned in another tab, but keep in mind the note written in clone voice")

                    with gr.Row():
                        speed = gr.Slider(minimum=0.5, maximum=2.0, value=1.0, label="Speed")
                        volume = gr.Slider(minimum=0, maximum=10, value=1.0, label="Volume")
                        pitch = gr.Slider(minimum=-12, maximum=12, value=0, step=1, label="Pitch")

                    # Additional parameters
                    emotion = gr.Dropdown(choices=HailuoTTS.EMOTIONS, label="Emotion", visible=False)
                    language = gr.Dropdown(choices=HailuoTTS.SUPPORTED_LANGUAGES, value="auto", label="Language Boost",info="Language Boost increases the accuracy of the voice, but only work with supported languages")

                    # Audio settings in accordion
                    with gr.Accordion("Audio Settings", open=True):
                        with gr.Row():
                            sample_rate = gr.Radio(
                                choices=HailuoTTS.AUDIO_CONSTRAINTS["sample_rate"],
                                value=HailuoTTS.AUDIO_CONSTRAINTS["sample_rate"][-1],
                                label="Sample Rate"
                            )
                            bitrate = gr.Radio(
                                choices=HailuoTTS.AUDIO_CONSTRAINTS["bitrate"],
                                value=HailuoTTS.AUDIO_CONSTRAINTS["bitrate"][-1],
                                label="Bitrate"
                            )
                        with gr.Row():
                            audio_format = gr.Radio(
                                choices=HailuoTTS.AUDIO_CONSTRAINTS["format"],
                                value=HailuoTTS.AUDIO_CONSTRAINTS["format"][0],
                                label="Format"
                            )
                            channel = gr.Radio(
                                choices=HailuoTTS.AUDIO_CONSTRAINTS["channel"],
                                value=HailuoTTS.AUDIO_CONSTRAINTS["channel"][0],
                                label="Channels"
                            )
                
                # Generation button and output
                with gr.Column():
                    tts_output = gr.Audio(label="Result")
                    tts_status = gr.Textbox(label="Status", interactive=False)
                    tts_btn = gr.Button("Generate")

        # Clone Voice tab
        with gr.Tab("Clone Voice"):
            gr.Markdown("""
            ### File Requirements:
            - Formats: MP3, M4A, WAV
            - Duration: 10s to 5min 
            - Size: Less than 20MB
            - Quality: Clear voice recording with minimal background noise
            - Content: Natural speech in any language
            """)
            
            with gr.Row():
                with gr.Column():
                    # Cloning parameters
                    audio_file = gr.File(label="Audio File", file_types=["audio"])
                    use_custom_voice_id = gr.Checkbox(label="Random Voice ID",value=True,info="If you check this checkbox, you will be able to use a custom voice ID")
                    voice_id = gr.Textbox(label="Voice ID",visible=False, placeholder="Minimum 8 characters, letters and numbers,first letter must be a letter")
                    
                    with gr.Row():
                        noise_reduction = gr.Checkbox(label="Noise Reduction", value=False)
                        volume_normalize = gr.Checkbox(label="Volume Normalization", value=False)
                
                    preview_text = gr.Textbox(label="Preview Text (max 300 characters)",max_length=300, value="Test voice", lines=2)
                    accuracy = gr.Slider(minimum=0, maximum=1, value=0.7, label="Accuracy")

                with gr.Column():
                    clone_output = gr.Audio(label="Preview")
                    clone_status = gr.Textbox(label="Status", interactive=False)
                    clone_btn = gr.Button("Clone")
            gr.Markdown("""
# Important Notes:
1. When you get a voice preview, it is synthesized using the turbo model.
2. You don't pay $3 for voice cloning. You only pay for synthesis.
3. You can copy the resulting ID and use it in the TTS tab. Please note that as soon as you use it at least once, you will be charged $3 for voice creation. It will be linked to your account. Make sure to save this ID somewhere to use it in TTS later.
4. Unverified voice cloning is free, but it life time is limited to 7 days.
""")
    
    # Event handlers
    auth_btn.click(
        authorize,
        inputs=[api_key, group_id],
        outputs=[tabs, auth_error]
    )
    
    model.change(
        on_model_change,
        inputs=[model],
        outputs=[emotion]
    )
    
    tts_btn.click(
        text_to_speech,
        inputs=[
            text_input, model, voice, speed, volume, pitch, emotion, language,
            sample_rate, bitrate, audio_format, channel
        ],
        outputs=[tts_output, tts_status]
    )
    
    clone_btn.click(
        clone_voice,
        inputs=[audio_file, voice_id, noise_reduction, preview_text, accuracy, volume_normalize,use_custom_voice_id],
        outputs=[clone_output, clone_status]
    )

    use_custom_voice_id.change(
        show_voice_id_input,
        inputs=[use_custom_voice_id],
        outputs=[voice_id]
    )
# Launch interface
if __name__ == "__main__":
    app.launch()