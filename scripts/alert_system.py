import os
import csv
import cv2
from datetime import datetime


class AlertSystem:
    """
    Handles violation alerts for the SafetyEye system.

    Responsibilities:
    1. Save violation logs into a CSV file
    2. Save screenshot evidence for violations
    3. Keep simple counters for session summary
    """

    def __init__(self):
        # Folder where screenshots of violation frames will be stored
        self.screenshot_folder = "violation_screenshots"

        # CSV file used by the dashboard
        self.log_file = "violations.csv"

        # Create screenshot folder if it does not exist
        os.makedirs(self.screenshot_folder, exist_ok=True)

        # Create CSV file with header if it does not exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["timestamp", "violation_type"])

        # Session-level counters
        self.violation_counts = {}
        self.total_violations = 0
        self.start_time = datetime.now()

    def trigger_alert(self, message, frame=None):
        """
        Trigger a violation alert.

        Args:
            message (str): Violation message, for example:
                           'No Hardhat detected on person'
            frame (numpy array, optional): Current video frame.
                                           If provided, it will be saved
                                           as screenshot evidence.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Update in-memory counters
        self.violation_counts[message] = self.violation_counts.get(message, 0) + 1
        self.total_violations += 1

        # Print alert in terminal
        print(f"[VIOLATION] {now} - {message}")

        # Save alert into CSV log
        with open(self.log_file, "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([now, message])

        # Save screenshot of violating frame if frame is available
        if frame is not None:
            safe_message = message.replace(" ", "_").replace("/", "_")
            safe_time = now.replace(":", "-").replace(" ", "_")
            image_name = f"{safe_time}_{safe_message}.jpg"
            image_path = os.path.join(self.screenshot_folder, image_name)
            cv2.imwrite(image_path, frame)