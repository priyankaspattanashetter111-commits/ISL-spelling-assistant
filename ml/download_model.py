"""Download Google's hand detector, not an ISL alphabet classifier."""
from pathlib import Path
from urllib.request import urlretrieve
target=Path(__file__).parent/'models'/'hand_landmarker.task'
target.parent.mkdir(parents=True,exist_ok=True)
urlretrieve('https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task',target)
print('Saved hand landmark detector:',target)
