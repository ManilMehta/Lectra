#!/bin/bash

# Lectra - AI-Powered Lecture Note Taker Setup Script
# This script sets up the environment and dependencies for Lectra

# Set up variables
VENV_DIR=".venv"
PYTHON_VERSION="python3"
WHISPER_CPP_REPO="https://github.com/ggerganov/whisper.cpp.git"
WHISPER_CPP_DIR="whisper.cpp"
WHISPER_MODEL="small"   # Change to "base", "medium", "large", etc. as needed
PYTHON_SCRIPT="main.py"

echo "📚 Lectra - AI-Powered Lecture Note Taker"
echo "=========================================="
echo ""

# Step 1: Check if Python is installed
if ! command -v $PYTHON_VERSION &>/dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.x to continue."
    exit 1
fi

# Step 2: Create a virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating a virtual environment in $VENV_DIR..."
    $PYTHON_VERSION -m venv $VENV_DIR
else
    echo "✓ Virtual environment already exists."
fi

# Step 3: Activate the virtual environment
echo "🔧 Activating the virtual environment..."
source $VENV_DIR/bin/activate

# Step 4: Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Step 5: Install Python dependencies
echo "📥 Installing required Python dependencies (requests, gradio)..."
pip install requests gradio --quiet

# Step 6: Install FFmpeg if not installed
if ! command -v ffmpeg &>/dev/null; then
    echo "🎬 FFmpeg is not installed. Installing FFmpeg..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # For MacOS using Homebrew
        if ! command -v brew &>/dev/null; then
            echo "❌ Homebrew is not installed. Please install Homebrew from https://brew.sh/ and rerun this script."
            exit 1
        fi
        brew install ffmpeg
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    fi
else
    echo "✓ FFmpeg is already installed."
fi

# Step 6.5: Install cmake and other build dependencies if not installed
if ! command -v cmake &>/dev/null; then
    echo "🔨 cmake is not installed. Installing cmake..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # For MacOS using Homebrew
        if ! command -v brew &>/dev/null; then
            echo "❌ Homebrew is not installed. Please install Homebrew from https://brew.sh/ and rerun this script."
            exit 1
        fi
        brew install cmake
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y cmake build-essential
    fi
else
    echo "✓ cmake is already installed."
fi

# Step 7: Install whisper.cpp if not already installed
if [ ! -d "$WHISPER_CPP_DIR" ]; then
    echo "🎙️  Cloning whisper.cpp repository..."
    git clone $WHISPER_CPP_REPO
else
    echo "✓ whisper.cpp directory already exists."
fi

# Step 8: Build whisper.cpp
echo "🔨 Building whisper.cpp..."
cd $WHISPER_CPP_DIR
if [ ! -f "main" ]; then
    make
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build whisper.cpp. Please check for errors."
        exit 1
    fi
else
    echo "✓ whisper.cpp is already built."
fi
cd ..

# Step 9: Download the Whisper model
if [ ! -f "./$WHISPER_CPP_DIR/models/ggml-$WHISPER_MODEL.bin" ]; then
    echo "📥 Downloading the '$WHISPER_MODEL' Whisper model for whisper.cpp..."
    ./$WHISPER_CPP_DIR/models/download-ggml-model.sh $WHISPER_MODEL
else
    echo "✓ Whisper model '$WHISPER_MODEL' already downloaded."
fi

# Step 10: Run the Python script
echo ""
echo "🚀 Starting Lectra..."
echo "=========================================="
echo ""
if [ -f "$PYTHON_SCRIPT" ]; then
    python "$PYTHON_SCRIPT"
else
    echo "❌ Python script '$PYTHON_SCRIPT' not found. Please ensure the script exists."
    exit 1
fi

# Optional: Deactivate environment after running script
deactivate

