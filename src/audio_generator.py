import os
import json
import asyncio
import edge_tts
from pydub import AudioSegment

# Define voices for our characters
VOICE_MAP = {
    "Alex": "en-US-AndrewNeural", # Male host
    "Jamie": "en-US-AvaNeural"    # Female expert
}

async def synthesize_line(text, voice, output_filename):
    """Generates a single line of dialogue using edge-tts."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_filename)

async def process_podcast_audio(script_path, output_path):
    """Reads the JSON script and generates the final mixed MP3."""
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return

    with open(script_path, "r", encoding="utf-8") as f:
        script_data = json.load(f)

    temp_files = []
    
    print("\n🎙️  Recording in studio... (Synthesizing voices)")
    
    for idx, line in enumerate(script_data):
        speaker = line.get("speaker", "Alex")
        text = line.get("text", "")
        
        # Fallback to Andrew if speaker is unknown
        voice = VOICE_MAP.get(speaker, "en-US-AndrewNeural") 
        
        temp_file = f"temp_{idx}.mp3"
        temp_files.append(temp_file)
        
        print(f"   ➤ Rendering {speaker}'s line {idx+1}/{len(script_data)}...")
        await synthesize_line(text, voice, temp_file)

    print("\n🎬 Mixing audio tracks...")
    combined_audio = AudioSegment.empty()
    
    for temp_file in temp_files:
        segment = AudioSegment.from_mp3(temp_file)
        # Add the dialogue segment + 300ms of silence for a natural pause
        combined_audio += segment + AudioSegment.silent(duration=300)

    # Export the final combined file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    combined_audio.export(output_path, format="mp3")
    
    # Clean up temporary files
    print("🧹 Cleaning up studio...")
    for temp_file in temp_files:
        if os.path.exists(temp_file):
            os.remove(temp_file)
            
    print(f"✅ Podcast is ready! Saved to: {output_path}")


def generate_podcast_mp3(script_path):
    # Synchronous wrapper to be called from main.py
    base_name = os.path.basename(script_path)
    audio_filename = base_name.replace("script_", "podcast_").replace(".json", ".mp3")
    output_path = f"data/podcast_outputs/{audio_filename}"
    
    # Run the async function using asyncio
    asyncio.run(process_podcast_audio(script_path, output_path))