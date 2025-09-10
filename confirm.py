import cv2
import os
import pandas as pd
from datetime import datetime
import re
import openpyxl
import pyttsx3

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Optional: Adjust speech speed

# -------------------- Setup --------------------
photo_folder = "attendance_photos"
if not os.path.exists(photo_folder):
    os.makedirs(photo_folder)

# Open webcam or IP camera
url = 0  # 0 for default webcam
cap = cv2.VideoCapture(url)
if not cap.isOpened():
    print("Error: Cannot access webcam.")
    exit()

print("Press 'c' to capture photo and mark attendance, 'q' to quit.")

# -------------------- Main Loop --------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("Warning: Failed to capture frame.")
        continue

    today_date = datetime.now().strftime("%Y-%m-%d")
    excel_file = f"Attendance_{today_date}.xlsx"

    # Load or create Excel file
    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file)
        except:
            df = pd.DataFrame(columns=["Serial No", "Name", "Timestamp"])
    else:
        df = pd.DataFrame(columns=["Serial No", "Name", "Timestamp"])

    total_attendance = len(df)
    cv2.putText(frame, f"Total Attendance Today: {total_attendance}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    cv2.imshow("Attendance System - Press 'c' to capture", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        name = input("Enter your name: ").strip()

        if not re.match(r'^[A-Za-z ]+$', name):
            print("Error: Name should contain only letters and spaces!")
            continue

        confirm = input(f"Confirm saving attendance for {name}? (y/n): ").lower()
        if confirm != 'y':
            print("Cancelled.")
            continue

        if not df[df['Name'].str.lower() == name.lower()].empty:
            print(f"Attendance for {name} has already been marked today!")
            continue

        serial_no = len(df) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        date_folder = os.path.join(photo_folder, today_date)
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)
        image_filename = f"{serial_no}_{name}_{datetime.now().strftime('%H%M%S')}.jpg"
        image_path = os.path.join(date_folder, image_filename)
        cv2.imwrite(image_path, frame)
        print(f"Photo saved: {image_path}")

        df = pd.concat([df, pd.DataFrame([{
            "Serial No": serial_no,
            "Name": name,
            "Timestamp": timestamp
        }])], ignore_index=True)

        try:
            df.to_excel(excel_file, index=False)
        except Exception as e:
            print("Error saving Excel file:", e)
            continue

        print(f"Attendance marked for {name} (Serial No: {serial_no}) at {timestamp}\n")

        # Show confirmation message on frame
        cv2.putText(frame, "Attendance marked successfully!", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Attendance System - Press 'c' to capture", frame)

        # Speak confirmation message
        engine.say(f"Attendance marked successfully for {name}")
        engine.runAndWait()

        # Wait briefly so user sees the message
        cv2.waitKey(1500)

    elif key == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
print("Attendance system closed.")
