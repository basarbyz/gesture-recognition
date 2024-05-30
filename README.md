# Gesture Recognition with Google Drive Integration

This project provides a solution for recognizing hand gestures and uploading the captured gesture images to Google Drive. The system uses a combination of computer vision techniques and Google Drive API to detect, capture, and store gesture images.

## Overview

This project is a part of a larger remote exam surveillance project. My role in this project was to build the gesture recognition system and implement the Google Drive uploader.

## Features

- **Gesture Recognition**: Utilizes MediaPipe to recognize hand gestures.
- **Google Drive Integration**: Automatically uploads captured gesture images to Google Drive.
- **Countdown Timer**: Provides a countdown before capturing the gesture to ensure accuracy.

## Setup

### Prerequisites

1. **Python 3.7+**
2. **Google Cloud Project**: Ensure you have a Google Cloud project with the Google Drive API enabled.
3. **Service Account**: Create a service account and download the JSON credentials file.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/basarbyz/gesture-recognition.git
   cd gesture-recognition

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt

3. Place the service account credentials JSON file in the project directory and name it `credentials.json`.

### Configuration

1. **Google Drive Folder**: Create a root folder in your Google Drive and note down its folder ID.
2. **Update Configuration**: Open `main.py` and update the `root_folder_id` with your root folder ID.

## Usage

Run the main script:

```bash
python main.py


