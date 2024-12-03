# Magic Hands - Hand Gesture Based Face Recognition

A system that uses hand gestures to trigger face recognition. It captures and saves face images, compares them with existing ones, and returns matching data images.

## Features
- Hand gesture detection using MediaPipe and OpenCV.
- Face recognition and matching with existing data.
- Communicates with a FastAPI backend for image saving and retrieval.
- Similar to Huawei's AirDrop feature, allows seamless file transfer through hand gestures.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mudasirhabib123/magic_hands.git
cd magic_hands
```

### 2. Create and activate a virtual environment

```
python -m venv venv
source venv/bin/activate  # macOS/Linux
.\venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```
pip install -r requirements.txt
```
### 4. Start the FastAPI server
```
fastapi dev server.py
```
### 5. Run the main script
```
python main.py
```
## Video Demonstration
Watch the working demo:
[Download Magic Hands Video](magic_hands.mp4)