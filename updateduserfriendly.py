import cv2
import os
import pandas as pd
from datetime import datetime
import re
import openpyxl

# -------------------- Setup --------------------
photo_folder = "attendance_photos"
if not os.path.exists(photo_folder):
    os.makedirs(photo_folder)

# Open webcam or IP camera
url = 0  # Default webcam
cap = cv2.VideoCapture(url)
if not cap.isOpened():
    print("[Error] Cannot access webcam.")
    exit()

print("\n🎯 Welcome to the  Attendance System")
print("👉 Press 'c' to capture your photo and mark attendance")
print("👉 Press 'q' to quit the system\n")

# -------------------- Main Loop --------------------
while True:
    ret, frame = cap.read()
    if not ret:
        print("[Warning] Failed to capture frame. Retrying...")
        continue

    # Create daily attendance file
    today_date = datetime.now().strftime("%Y-%m-%d")
    excel_file = f"Attendance_{today_date}.xlsx"

    if os.path.exists(excel_file):
        try:
            df = pd.read_excel(excel_file)
        except:
            df = pd.DataFrame(columns=["Serial No", "Name", "Timestamp"])
    else:
        df = pd.DataFrame(columns=["Serial No", "Name", "Timestamp"])

    total_attendance = len(df)
    cv2.putText(frame, f"Total Attendance Today: {total_attendance}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    cv2.imshow("Attendance System - Press 'c' to capture, 'q' to quit", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        print("\n📋 Please enter your name (letters and spaces only):")
        name = input("🔹 Name: ").strip()

        if not re.match(r'^[A-Za-z ]+$', name):
            print("[Error] Invalid name. Only letters and spaces are allowed.")
            continue

        confirm = input(f"✅ Confirm marking attendance for '{name}'? (y/n): ").lower()
        if confirm != 'y':
            print("[Info] Attendance marking cancelled.\n")
            continue

        # Check for duplicates
        if not df[df['Name'].str.lower() == name.lower()].empty:
            print(f"[Info] Attendance already marked for {name} today!\n")
            continue

        serial_no = len(df) + 1
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        date_folder = os.path.join(photo_folder, today_date)
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        image_filename = f"{serial_no}_{name}_{datetime.now().strftime('%H%M%S')}.jpg"
        image_path = os.path.join(date_folder, image_filename)
        cv2.imwrite(image_path, frame)

        df = pd.concat([df, pd.DataFrame([{
            "Serial No": serial_no,
            "Name": name,
            "Timestamp": timestamp
        }])], ignore_index=True)

        try:
            df.to_excel(excel_file, index=False)
        except Exception as e:
            print(f"[Error] Failed to save Excel file: {e}")
            continue

        print(f"✅ Attendance successfully marked for {name} at {timestamp}\n")

        # Show success message on webcam feed
        cv2.putText(frame, f"Attendance marked for {name}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.imshow("Attendance System - Press 'c' to capture, 'q' to quit", frame)
        cv2.waitKey(1500)  # Show message for 1.5 seconds

    elif key == ord('q'):
        print("\n🚀 Exiting Attendance System. Have a nice day!")
        break

# -------------------- Cleanup --------------------
cap.release()
cv2.destroyAllWindows()
print("\n✅ System closed successfully.")
