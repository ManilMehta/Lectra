# 📚 Lectra - AI-Powered Lecture Note Taker

## Overview

**Lectra** is an intelligent Gradio-powered application that converts lecture audio recordings into comprehensive, structured notes and study flashcards. Built with `whisper.cpp` for accurate audio-to-text conversion and `Ollama` (Llama 3.2) for intelligent note and flashcard generation, Lectra helps students transform their lecture recordings into effective study materials.

## Features

- **🎤 Audio-to-Text Conversion**: Uses `whisper.cpp` to accurately transcribe lecture audio files into text
- **📖 Intelligent Note Generation**: Uses models from the `Ollama` server to create well-structured, comprehensive lecture notes with:
  - Clear headings and subheadings
  - Key concepts and definitions
  - Important examples and explanations
  - Main points and takeaways
  - Formulas, equations, and technical details
- **🃏 Flashcard Generation**: Automatically creates study flashcards from lecture content with:
  - Questions/terms on the front
  - Detailed answers/explanations on the back
  - Focus on key definitions, concepts, and takeaways
- **🎨 Modern UI**: Beautiful, intuitive interface with custom styling and organized tabs
- **📥 Export Options**: Download transcripts, notes, and flashcards for offline study
- **🔧 Multiple Models Support**: Supports different Whisper models (`base`, `small`, `medium`, `large-V3`) and any available model from the Ollama server

## Requirements

- Python 3.x
- [FFmpeg](https://www.ffmpeg.org/) (for audio processing)
- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) (for audio-to-text conversion)
- [Ollama server](https://ollama.com/) (for note and flashcard generation)
- [Gradio](https://www.gradio.app/) (for the web interface)
- [Requests](https://requests.readthedocs.io/en/latest/) (for handling API calls to the Ollama server)

## Pre-Installation

Before running Lectra, ensure you have Ollama running on your local machine or a server. You can follow the instructions provided in the [Ollama repository](https://github.com/ollama/ollama) to set up the server. Don't forget to download and run a model from the Ollama server.

```bash
# To install and run Llama 3.2
ollama run llama3.2
```

## Installation

Follow the steps below to set up and run Lectra:

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/Lectra
cd Lectra
```

### Step 2: Run the Setup Script

To install all necessary dependencies (including Python virtual environment, `whisper.cpp`, FFmpeg, and Python packages), and to run the application, execute the provided setup script:

```bash
chmod +x run_lectra.sh
./run_lectra.sh
```

This script will:

- Create and activate a Python virtual environment
- Install necessary Python packages like `requests` and `gradio`
- Check if `FFmpeg` is installed and install it if missing
- Clone and build `whisper.cpp`
- Download the required Whisper model (default: `small`)
- **Run the `main.py` script**, which will start the Gradio interface for Lectra

### Step 3: Accessing Lectra

Once the setup and execution are complete, Gradio will provide a URL (typically `http://127.0.0.1:7860`). Open this URL in your web browser to access the Lectra interface.

Alternatively, after setup, you can activate the virtual environment and run the Python script manually:

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the main.py script
python main.py
```

## Usage

### Processing a Lecture Recording

1. **Upload an Audio File**: Click on the audio upload area and select a lecture recording in any supported format (e.g., `.wav`, `.mp3`, `.m4a`).

2. **Provide Context (Optional)**: Add context about the course or subject (e.g., "Introduction to Machine Learning, Week 3") to help generate more accurate notes.

3. **Select Models**:
   - **Whisper Model**: Choose one of the available Whisper models (`base`, `small`, `medium`, `large-V3`) for audio-to-text conversion. Larger models are more accurate but slower.
   - **LLM Model**: Choose a model from the available options retrieved from the `Ollama` server for note and flashcard generation.

4. **Generate Flashcards**: Check the "Generate Flashcards" checkbox if you want flashcards created from the lecture.

5. **Process**: Click the "🚀 Process Lecture" button to start processing.

### Viewing Results

After processing, you'll see three tabs:

- **📖 Lecture Notes**: Comprehensive, structured notes from your lecture
- **🃏 Flashcards**: Study flashcards with questions and answers (if generated)
- **📄 Transcript**: Download the full transcript as a text file

You can copy the notes and flashcards directly from the interface or download the transcript file.

## Customization

### Changing the Whisper Model

By default, the Whisper model used is `small`. You can modify this in the `run_lectra.sh` script by changing the `WHISPER_MODEL` variable:

```bash
WHISPER_MODEL="medium"
```

Alternatively, you can select different Whisper models from the dropdown in the Gradio interface. The list of available models is dynamically generated based on the `.bin` files found in the `whisper.cpp/models` directory.

### Downloading Additional Whisper Models

To download a different Whisper model (e.g., `base`, `medium`, `large`), use the following steps:

1. Navigate to the `whisper.cpp` directory:

   ```bash
   cd whisper.cpp
   ```

2. Use the provided script to download the desired model. For example, to download the `base` model, run:

   ```bash
   ./models/download-ggml-model.sh base
   ```

   For the `large` model, you can run:

   ```bash
   ./models/download-ggml-model.sh large
   ```

   This will download the `.bin` file into the `whisper.cpp/models` directory.

3. Once downloaded, the new model will automatically be available in the model dropdown when you restart Lectra.

## Tips for Best Results

1. **Provide Context**: Adding course/subject context helps the AI generate more relevant and accurate notes
2. **Use Higher Quality Models**: For better accuracy, use `medium` or `large-V3` Whisper models (though they're slower)
3. **Clear Audio**: Ensure your lecture recordings have clear audio for best transcription results
4. **Review and Edit**: Always review the generated notes and flashcards, as AI-generated content may need refinement

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements

- **whisper.cpp** by Georgi Gerganov for the audio-to-text conversion
- **Gradio** for the interactive web interface framework
- **Ollama** for providing large language models for note and flashcard generation
- **Llama 3.2** by Meta for the language model capabilities

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
