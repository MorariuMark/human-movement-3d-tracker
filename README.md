Computer vision system developed in Python for tracking human movement in 3D space and recognizing calibration gestures using a standard 2D webcam and MediaPipe.

# Interactive 3D Human Movement Tracker

## Description
This project is a Computer Vision application developed in Python, designed to estimate a person's position in a three-dimensional space using a single standard webcam (2D). The application utilizes the MediaPipe library to detect body keypoints and applies the Pinhole Camera geometric model to calculate the real physical distance in meters from the optical sensor.

The project is highly useful for subject monitoring applications, interactive control systems, or biomechanics experiments where hardware depth sensors (such as LiDAR or Infrared cameras) are not available.

## Main Features
- Real-time estimation of X (horizontal) and Z (depth) spatial coordinates.
- Touchless control: Resetting and calibrating the origin point (0.00m) is executed entirely via hand gestures.
- Automatic spatial calibration based on the average biometric shoulder width of a human (0.40m).
- Native support for high resolution (1080p) and Full-Screen display for better visibility from a distance.
- Clean user interface achieved by intentionally hiding unnecessary facial landmarks during tracking.

## Technologies Used
- Python 3.12
- OpenCV (Video capture, matrix manipulation, and UI rendering)
- MediaPipe (Pose Estimation via neural networks)

## System Requirements
- Webcam (integrated or external).
- Operating System: Windows, macOS, or Linux.
- Python 3.10 or newer.

## Installation

1. Clone this repository:
git clone https://github.com/your-username/human-movement-3d-tracker.git
cd human-movement-3d-tracker

2. Create and activate a virtual environment (recommended):
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

3. Install the required dependencies:
pip install opencv-python mediapipe protobuf==4.25.3

## Usage

1. Start the application:
python tracker.py

2. Calibrate the origin point:
Stand in front of the camera and raise either hand above the level of your head. The system will recognize the gesture and set your current physical position as the center (0.00m, 0.00m). The message "CENTER RESET!" will appear on the screen to confirm the action.

3. Movement monitoring:
After calibration, move left, right, forward, or backward. The screen will dynamically display your distance in meters and the direction of your movement relative to the established origin point.

4. Closing the application:
Press the 'q' key on your keyboard to stop the video feed and close the window safely.

## Technical Details and Methodology
The system compensates for the lack of a hardware depth sensor by measuring the variation of the user's shoulder width in pixels. As the user moves further away from the camera, the shoulder width in pixels decreases. This inversely proportional relationship allows the algorithm to calculate the physical distance on the Z-axis, using the focal length of the camera lens as a calibration constant.

## Author
Morariu Christian-Mark
