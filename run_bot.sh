#!/bin/bash

# Video Tools Bot Startup Script

echo "🎬 Starting Video Tools Bot..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Run 'python setup.py' to configure the bot first."
    exit 1
fi

# Check if downloads directory exists
if [ ! -d "downloads" ]; then
    echo "📁 Creating downloads directory..."
    mkdir -p downloads
fi

# Check FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found!"
    echo "Install with: sudo apt install ffmpeg"
    exit 1
fi

echo "✅ All checks passed!"
echo "🚀 Launching bot..."
echo ""

# Run the bot
python main.py
