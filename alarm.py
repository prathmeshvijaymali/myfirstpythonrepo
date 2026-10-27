import time
from datetime import datetime
import winsound

# Set alarm time in 24-hour format
alarm_time = input("Enter alarm time (HH:MM:SS): ")

print(f"Alarm set for {alarm_time}")

while True:
    current_time = datetime.now().strftime("%H:%M:%S")

    if current_time == alarm_time:
        print("⏰ WAKE UP! ALARM RINGING!")

        # Play alarm sound
        for _ in range(10):
            winsound.Beep(1000, 500)
            time.sleep(0.2)

        break

    time.sleep(1)
