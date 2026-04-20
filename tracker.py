import cv2
import mediapipe as mp

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# --- CALIBRATION CONSTANTS ---
REAL_SHOULDER_WIDTH_M = 0.40 
FOCAL_LENGTH_PX = 600 

def main():
    cap = cv2.VideoCapture(0)
    
    # --- UPGRADE CAMERA RESOLUTION ---
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    
    # Store "Center" starting position
    origin_x_m = None
    origin_z_m = None

    print("Raise EITHER HAND above your head to set/reset the center point.")
    print("Press 'q' to quit.")

    # --- FULL SCREEN CONFIGURATION ---
    cv2.namedWindow("Movement Tracker", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Movement Tracker", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame horizontally so it acts like a mirror
        frame = cv2.flip(frame, 1)
        h, w_img, _ = frame.shape

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark

            # --- HIDE THE FACE LANDMARKS ---
            for i in range(11):
                landmarks[i].visibility = 0.0

            # Draw the skeleton (face will now be invisible)
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # 1. Get Landmarks for Shoulders, Nose, and BOTH Wrists
            l_sh = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            r_sh = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            nose = landmarks[mp_pose.PoseLandmark.NOSE]
            r_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            l_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST] # Added left wrist

            # Convert to pixel coordinates
            l_sh_x, _ = int(l_sh.x * w_img), int(l_sh.y * h)
            r_sh_x, _ = int(r_sh.x * w_img), int(r_sh.y * h)

            pixel_shoulder_width = abs(l_sh_x - r_sh_x)

            if pixel_shoulder_width > 0:
                # 2. Calculate Current Position
                current_z_m = (REAL_SHOULDER_WIDTH_M * FOCAL_LENGTH_PX) / pixel_shoulder_width
                mid_x_px = (l_sh_x + r_sh_x) / 2
                current_x_m = ((mid_x_px - w_img/2) * current_z_m) / FOCAL_LENGTH_PX

                # --- GESTURE RECOGNITION LOGIC (BOTH HANDS) ---
                # If either the right wrist OR the left wrist is higher than the nose
                if r_wrist.y < nose.y or l_wrist.y < nose.y:
                    origin_x_m = current_x_m
                    origin_z_m = current_z_m
                    
                    cv2.putText(frame, "CENTER RESET!", (int(w_img/2) - 150, int(h/2)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 4)

                if origin_x_m is None:
                    origin_x_m = current_x_m
                    origin_z_m = current_z_m

                # 3. Calculate movement relative to the origin
                move_x = current_x_m - origin_x_m
                move_z = current_z_m - origin_z_m

                dir_x = "Right" if move_x > 0 else "Left"
                dir_z = "Backward" if move_z > 0 else "Forward"

                text_x = f"Horizontal: {abs(move_x):.2f}m {dir_x}"
                text_z = f"Depth: {abs(move_z):.2f}m {dir_z}"

                # 4. Display the text (Made larger)
                # Expanded the background box to 450x100 to fit the bigger text
                cv2.rectangle(frame, (10, 10), (450, 100), (0, 0, 0), -1) 
                
                # Increased font scale back up to 1.0 and adjusted spacing
                cv2.putText(frame, text_x, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.putText(frame, text_z, (20, 85), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)

        cv2.imshow("Movement Tracker", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()


    