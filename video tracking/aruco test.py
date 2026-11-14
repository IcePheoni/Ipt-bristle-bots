import cv2
import numpy as np

# 1. Load the 4x4 (50) dictionary to match chev.me/arucogen
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

# 2. Open your laptop's default webcam (index 0).
# DirectShow avoids the black-frame issue that can occur with the default
# Windows Media Foundation backend.
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap.release()
    raise RuntimeError("Could not open the webcam. Check camera permissions and that it is not in use.")

# MJPG is supported by most webcams and prevents some Windows drivers from
# returning a stream of black frames.
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

print("Hold your phone screen up to the webcam. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        cap.release()
        cv2.destroyAllWindows()
        raise RuntimeError("Could not read a frame from the webcam.")

    # 3. Detect markers in the current video frame
    corners, ids, rejected = detector.detectMarkers(frame)

    if ids is not None:
        # Draw the green bounding box and ID number on screen
        cv2.aruco.drawDetectedMarkers(frame, corners, ids)

        for i, marker_id in enumerate(ids.flatten()):
            # Extract the 4 corner pixel coordinates: top-left, top-right, bottom-right, bottom-left
            pts = corners[i][0]
            
            # Center (x, y) is the average of the 4 corners
            cx, cy = int(pts[:, 0].mean()), int(pts[:, 1].mean())
            
            # Orientation angle (theta) from bottom-left (pts[3]) to top-left (pts[0])
            dx = pts[0][0] - pts[3][0]
            dy = pts[0][1] - pts[3][1]
            theta_deg = np.degrees(np.arctan2(dy, dx))

            print(f"ID: {marker_id} | Center: ({cx}, {cy}) px | Angle: {theta_deg:.1f}°")

    cv2.imshow("ArUco Webcam Test", frame)

    # Press 'q' to close the window
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()