# utils/face_utils.py

import os
import cv2
import face_recognition
from datetime import datetime
import pandas as pd
from geopy.distance import geodesic
import uuid

def load_student_images(path):
    encodings = []
    names = []

    for filename in os.listdir(path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join(path, filename)
            img = face_recognition.load_image_file(filepath)
            faces = face_recognition.face_encodings(img)
            if faces:
                encodings.append(faces[0])
                names.append(os.path.splitext(filename)[0])
            else:
                print(f"[WARNING] No face found in {filename}")
    return encodings, names

def mark_attendance(name, attendance_dict):
    if name not in attendance_dict:
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        attendance_dict[name] = now
        print(f"[ATTENDANCE] {name} marked at {now}")

def start_attendance(known_encodings, known_names, teacher_location):
    attendance = {}

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not access webcam.")
        return

    print("[INFO] Press 'q' to stop attendance.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Camera read failed.")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small)
        face_encodings = face_recognition.face_encodings(rgb_small, face_locations)

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.45)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            best_match_index = face_distances.argmin()

            top, right, bottom, left = [v * 4 for v in face_location]

            if matches[best_match_index] and face_distances[best_match_index] < 0.45:
                name = known_names[best_match_index]

                student_location = teacher_location  # use same location check logic
                if student_location:
                    distance = geodesic(teacher_location, student_location).meters
                    if distance <= 10:
                        mark_attendance(name, attendance)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, name, (left, top - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Face Attendance - Press 'q' to stop", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    df = pd.DataFrame(list(attendance.items()), columns=["Name", "Timestamp"])
    df.to_csv("Attendance.csv", index=False)
    print("[INFO] Attendance saved to Attendance.csv")
