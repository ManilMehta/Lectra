import subprocess
import os
import gradio as gr
import requests
import json
import re
from pathlib import Path

# Get the absolute path of the script's directory
SCRIPT_DIR = Path(__file__).parent.absolute()

OLLAMA_SERVER_URL = "http://localhost:11434"  # Replace this with your actual Ollama server URL if different
WHISPER_MODEL_DIR = SCRIPT_DIR / "whisper.cpp" / "models"  # Directory where whisper models are stored

# Try to find whisper binary in common locations (prefer whisper-cli over deprecated main)
WHISPER_BINARY = None
possible_binary_paths = [
    SCRIPT_DIR / "whisper.cpp" / "build" / "bin" / "whisper-cli",  # CMake build location (preferred)
    SCRIPT_DIR / "whisper.cpp" / "build" / "bin" / "main",  # CMake build location (deprecated)
    SCRIPT_DIR / "whisper.cpp" / "main",  # Direct make build location (deprecated)
]

for binary_path in possible_binary_paths:
    if binary_path.exists() and os.access(binary_path, os.X_OK):
        WHISPER_BINARY = binary_path
        break

if WHISPER_BINARY is None:
    # Set a default path for error messages
    WHISPER_BINARY = possible_binary_paths[0]


def get_available_models() -> list[str]:
    """
    Retrieves a list of all available models from the Ollama server and extracts the model names.

    Returns:
        A list of model names available on the Ollama server.
    """
    response = requests.get(f"{OLLAMA_SERVER_URL}/api/tags")
    if response.status_code == 200:
        models = response.json()["models"]
        llm_model_names = [model["model"] for model in models]  # Extract model names
        return llm_model_names
    else:
        raise Exception(
            f"Failed to retrieve models from Ollama server: {response.text}"
        )


def get_available_whisper_models() -> list[str]:
    """
    Retrieves a list of available Whisper models based on downloaded .bin files in the whisper.cpp/models directory.
    Filters out test models and only includes official Whisper models (e.g., base, small, medium, large).

    Returns:
        A list of available Whisper model names (e.g., 'base', 'small', 'medium', 'large-V3').
    """
    # List of acceptable official Whisper models
    valid_models = ["base", "small", "medium", "large", "large-V3"]

    # Get the list of model files in the models directory
    if not WHISPER_MODEL_DIR.exists():
        return []
    
    model_files = [f.name for f in WHISPER_MODEL_DIR.iterdir() if f.suffix == ".bin"]

    # Filter out test models and models that aren't in the valid list
    whisper_models = [
        f.replace("ggml-", "").replace(".bin", "")
        for f in model_files
        if any(valid_model in f for valid_model in valid_models) and "test" not in f
    ]

    # Remove any potential duplicates
    whisper_models = list(set(whisper_models))

    return whisper_models


def generate_lecture_notes(llm_model_name: str, context: str, text: str) -> str:
    """
    Uses a specified model on the Ollama server to generate structured lecture notes.
    Handles streaming responses by processing each line of the response.

    Args:
        llm_model_name (str): The name of the model to use for note generation.
        context (str): Optional context for the notes, provided by the user.
        text (str): The transcript text to convert into notes.

    Returns:
        str: The generated lecture notes from the model.
    """
    prompt = f"""You are an expert note-taking assistant. You are given a transcript from a lecture, along with some optional context.
    
    Context: {context if context else 'No additional context provided.'}
    
    The transcript is as follows:
    
    {text}
    
    Please create comprehensive, well-organized lecture notes from this transcript. Structure the notes with:
    - Clear headings and subheadings
    - Key concepts and definitions
    - Important examples and explanations
    - Main points and takeaways
    - Any formulas, equations, or technical details mentioned
    
    Format the notes in a clear, hierarchical structure that would be useful for studying."""

    headers = {"Content-Type": "application/json"}
    data = {"model": llm_model_name, "prompt": prompt}

    response = requests.post(
        f"{OLLAMA_SERVER_URL}/api/generate", json=data, headers=headers, stream=True
    )

    if response.status_code == 200:
        full_response = ""
        try:
            # Process the streaming response line by line
            for line in response.iter_lines():
                if line:
                    # Decode each line and parse it as a JSON object
                    decoded_line = line.decode("utf-8")
                    json_line = json.loads(decoded_line)
                    # Extract the "response" part from each JSON object
                    full_response += json_line.get("response", "")
                    # If "done" is True, break the loop
                    if json_line.get("done", False):
                        break
            return full_response
        except json.JSONDecodeError:
            print("Error: Response contains invalid JSON data.")
            return f"Failed to parse the response from the server. Raw response: {response.text}"
    else:
        raise Exception(
            f"Failed to generate notes with model {llm_model_name}: {response.text}"
        )


def generate_flashcards(llm_model_name: str, context: str, text: str) -> str:
    """
    Uses a specified model on the Ollama server to generate flashcards from the lecture transcript.
    Handles streaming responses by processing each line of the response.

    Args:
        llm_model_name (str): The name of the model to use for flashcard generation.
        context (str): Optional context for the flashcards, provided by the user.
        text (str): The transcript text to convert into flashcards.

    Returns:
        str: The generated flashcards in a structured format.
    """
    prompt = f"""You are an expert at creating study flashcards. You are given a transcript from a lecture, along with some optional context.
    
    Context: {context if context else 'No additional context provided.'}
    
    The transcript is as follows:
    
    {text}
    
    Please create flashcards from this lecture transcript. For each important concept, term, definition, or key point, create a flashcard with:
    - A clear question or term on the front
    - A detailed answer or explanation on the back
    
    Format each flashcard as follows:
    
    **Front:** [Question or Term]
    **Back:** [Answer or Explanation]
    
    ---
    
    Create at least 10-15 flashcards covering the most important concepts from the lecture. Focus on:
    - Key definitions and terminology
    - Important concepts and theories
    - Formulas or equations (if applicable)
    - Examples and applications
    - Main takeaways and conclusions"""

    headers = {"Content-Type": "application/json"}
    data = {"model": llm_model_name, "prompt": prompt}

    response = requests.post(
        f"{OLLAMA_SERVER_URL}/api/generate", json=data, headers=headers, stream=True
    )

    if response.status_code == 200:
        full_response = ""
        try:
            # Process the streaming response line by line
            for line in response.iter_lines():
                if line:
                    # Decode each line and parse it as a JSON object
                    decoded_line = line.decode("utf-8")
                    json_line = json.loads(decoded_line)
                    # Extract the "response" part from each JSON object
                    full_response += json_line.get("response", "")
                    # If "done" is True, break the loop
                    if json_line.get("done", False):
                        break
            return full_response
        except json.JSONDecodeError:
            print("Error: Response contains invalid JSON data.")
            return f"Failed to parse the response from the server. Raw response: {response.text}"
    else:
        raise Exception(
            f"Failed to generate flashcards with model {llm_model_name}: {response.text}"
        )


def preprocess_audio_file(audio_file_path: str) -> str:
    """
    Converts the input audio file to a WAV format with 16kHz sample rate and mono channel.

    Args:
        audio_file_path (str): Path to the input audio file.

    Returns:
        str: The path to the preprocessed WAV file.
    """
    output_wav_file = f"{os.path.splitext(audio_file_path)[0]}_converted.wav"

    # Ensure ffmpeg converts to 16kHz sample rate and mono channel
    cmd = f'ffmpeg -y -i "{audio_file_path}" -ar 16000 -ac 1 "{output_wav_file}"'
    subprocess.run(cmd, shell=True, check=True)

    return output_wav_file


def process_lecture_audio(
    audio_file_path: str, context: str, whisper_model_name: str, llm_model_name: str, generate_flashcards_flag: bool
) -> tuple[str, str, str]:
    """
    Transcribes the audio file into text using the whisper.cpp model and generates lecture notes and flashcards using Ollama.
    Also provides the transcript file for download.

    Args:
        audio_file_path (str): Path to the input audio file.
        context (str): Optional context to include in the notes.
        whisper_model_name (str): Whisper model to use for audio-to-text conversion.
        llm_model_name (str): Model to use for generating notes and flashcards.
        generate_flashcards_flag (bool): Whether to generate flashcards or not.

    Returns:
        tuple[str, str, str]: A tuple containing the notes, flashcards (or empty string), and the path to the transcript file for download.
    """
    output_file = "output.txt"

    print("Processing audio file:", audio_file_path)

    # Convert the input file to WAV format if necessary
    audio_file_wav = preprocess_audio_file(audio_file_path)

    print("Audio preprocessed:", audio_file_wav)

    # Check if whisper binary exists (re-check in case it was built after script start)
    whisper_binary = None
    possible_binary_paths = [
        SCRIPT_DIR / "whisper.cpp" / "build" / "bin" / "whisper-cli",  # CMake build location (preferred)
        SCRIPT_DIR / "whisper.cpp" / "build" / "bin" / "main",  # CMake build location (deprecated)
        SCRIPT_DIR / "whisper.cpp" / "main",  # Direct make build location (deprecated)
    ]
    
    for binary_path in possible_binary_paths:
        if binary_path.exists() and os.access(binary_path, os.X_OK):
            whisper_binary = binary_path
            break
    
    if whisper_binary is None:
        raise FileNotFoundError(
            f"Whisper binary not found. Tried: {', '.join(str(p) for p in possible_binary_paths)}. "
            "Please ensure whisper.cpp is built. Run: cd whisper.cpp && make (or cmake build)"
        )
    
    # Get absolute paths for model and output file
    model_path = WHISPER_MODEL_DIR / f"ggml-{whisper_model_name}.bin"
    if not model_path.exists():
        raise FileNotFoundError(
            f"Whisper model not found at {model_path}. "
            f"Please download the model first."
        )
    
    output_file_path = SCRIPT_DIR / output_file
    
    # Call the whisper.cpp binary using absolute paths
    # whisper-cli uses -m for model, -f for file, and outputs to stdout by default
    whisper_command = [
        str(whisper_binary),
        "-m", str(model_path),
        "-f", audio_file_wav,
        "-nt",  # No timestamps for cleaner output
    ]
    
    # Run whisper and capture output
    try:
        with open(output_file_path, "w") as outfile:
            result = subprocess.run(
                whisper_command,
                stdout=outfile,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else "Unknown error"
        raise RuntimeError(
            f"Whisper transcription failed: {error_msg}\n"
            f"Command: {' '.join(whisper_command)}"
        )

    print("Whisper.cpp executed successfully")

    # Read the output from the transcript
    with open(output_file_path, "r") as f:
        transcript = f.read()

    # Save the transcript to a downloadable file
    transcript_file_path = SCRIPT_DIR / "transcript.txt"
    with open(transcript_file_path, "w") as transcript_f:
        transcript_f.write(transcript)

    # Generate lecture notes from the transcript using Ollama's model
    notes = generate_lecture_notes(llm_model_name, context, transcript)
    
    # Generate flashcards if requested
    flashcards = ""
    if generate_flashcards_flag:
        flashcards = generate_flashcards(llm_model_name, context, transcript)

    # Clean up temporary files
    if os.path.exists(audio_file_wav):
        os.remove(audio_file_wav)
    if output_file_path.exists():
        os.remove(output_file_path)

    # Return the notes, flashcards, and downloadable link for the transcript
    return notes, flashcards, str(transcript_file_path)


# Gradio interface
def gradio_app(
    audio, context: str, whisper_model_name: str, llm_model_name: str, generate_flashcards_flag: bool
) -> tuple[str, str, str]:
    """
    Gradio application to handle file upload, model selection, and note/flashcard generation.

    Args:
        audio: The uploaded audio file.
        context (str): Optional context provided by the user.
        whisper_model_name (str): The selected Whisper model name.
        llm_model_name (str): The selected language model for note generation.
        generate_flashcards_flag (bool): Whether to generate flashcards.

    Returns:
        tuple[str, str, str]: A tuple containing the notes, flashcards, and a downloadable transcript file.
    """
    return process_lecture_audio(audio, context, whisper_model_name, llm_model_name, generate_flashcards_flag)


# Custom CSS theme for Lectra
custom_css = """
    .gradio-container {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    .output-box {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
    }
    .flashcard-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 8px;
        padding: 1rem;
    }
"""

# Main function to launch the Gradio interface
if __name__ == "__main__":
    # Retrieve available models for Gradio dropdown input
    ollama_models = get_available_models()  # Retrieve models from Ollama server
    whisper_models = (
        get_available_whisper_models()
    )  # Dynamically detect downloaded Whisper models

    # Ensure the first model is selected by default
    with gr.Blocks(css=custom_css, theme=gr.themes.Soft(primary_hue="purple")) as iface:
        gr.HTML("""
            <div class="main-header">
                <h1>📚 Lectra</h1>
                <p>AI-Powered Lecture Note Taker & Flashcard Generator</p>
            </div>
        """)
        
        gr.Markdown("""
        ### Transform your lectures into comprehensive notes and study flashcards
        
        Upload a lecture recording and let Lectra convert it into structured notes and flashcards to help you study more effectively.
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.Audio(
                    type="filepath", 
                    label="🎤 Upload Lecture Audio",
                    elem_classes=["input-box"]
                )
                context_input = gr.Textbox(
                    label="📝 Course/Subject Context (optional)",
                    placeholder="e.g., Introduction to Machine Learning, Week 3",
                    lines=2,
                )
                generate_flashcards_checkbox = gr.Checkbox(
                    label="Generate Flashcards",
                    value=True,
                    info="Create study flashcards from the lecture"
                )
                
            with gr.Column(scale=1):
                whisper_model_dropdown = gr.Dropdown(
                    choices=whisper_models,
                    label="🎙️ Whisper Model (Speech-to-Text)",
                    value=whisper_models[0] if whisper_models else None,
                    info="Select the model for audio transcription"
                )
                llm_model_dropdown = gr.Dropdown(
                    choices=ollama_models,
                    label="🤖 LLM Model (Note Generation)",
                    value=ollama_models[0] if ollama_models else None,
                    info="Select the model for generating notes and flashcards"
                )
        
        process_btn = gr.Button("🚀 Process Lecture", variant="primary", size="lg")
        
        with gr.Tabs():
            with gr.Tab("📖 Lecture Notes"):
                notes_output = gr.Textbox(
                    label="Generated Notes",
                    lines=20,
                    elem_classes=["output-box"]
                )
            
            with gr.Tab("🃏 Flashcards"):
                flashcards_output = gr.Textbox(
                    label="Generated Flashcards",
                    lines=20,
                    elem_classes=["flashcard-box"]
                )
            
            with gr.Tab("📄 Transcript"):
                transcript_output = gr.File(
                    label="Download Full Transcript"
                )
        
        gr.Markdown("""
        ---
        ### How it works:
        1. **Upload** your lecture audio file (any format supported)
        2. **Provide context** about the course/subject (optional but recommended)
        3. **Select models** for transcription and note generation
        4. **Click Process** to generate notes and flashcards
        5. **Download** your transcript, notes, and flashcards
        
        *Powered by Whisper.cpp and Ollama (Llama 3.2)*
        """)
        
        process_btn.click(
            fn=gradio_app,
            inputs=[audio_input, context_input, whisper_model_dropdown, llm_model_dropdown, generate_flashcards_checkbox],
            outputs=[notes_output, flashcards_output, transcript_output]
        )

    iface.launch(debug=True, share=False)
