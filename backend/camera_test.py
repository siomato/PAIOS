import cv2

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ Camera failed to open")
    raise SystemExit

print("✅ Camera opened successfully")
print("📷 Live camera test started")
print("Press Q to quit")

while True:

    ret, frame = camera.read()

    if not ret:
        print("❌ Failed to read camera frame")
        break

    cv2.imshow("PAIOS CAMERA TEST", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print("✅ Camera test finished")