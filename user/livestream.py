from django.http import HttpResponseServerError, StreamingHttpResponse
from django.views.decorators import gzip
import cv2

cascade_path = 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascade_path)
video_capture = cv2.VideoCapture(0)

class LiveStream:
    def __init__(self):
        self.streaming_flag = True

    def recognize_faces_generator(self):
        while self.streaming_flag:
            ret, frame = video_capture.read()
            if not ret:
                raise RuntimeError("Failed to capture image")

            # Mirror the frame horizontally
            frame = cv2.flip(frame, 1)

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for idx, (x, y, w, h) in enumerate(faces):
                # Filter out small detections
                if w * h < 1000:
                    continue

                # Draw rectangle and label only if the detection is significant
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green rectangle
                cv2.putText(frame, f"Face {idx + 1}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if len(faces) == 1:  # Only one face detected
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            elif len(faces) > 1:  # More than one face detected
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)  # Change color to red
                cv2.putText(frame, "Error: More than one face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                            (0, 0, 255), 2)
            else:  # No face detected
                cv2.putText(frame, "Error: No face detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            _, jpeg = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

    def start_streaming(self):
        try:
            return StreamingHttpResponse(self.recognize_faces_generator(), content_type="multipart/x-mixed-replace;boundary=frame")
        except Exception as e:
            print("Error:", e)
            return HttpResponseServerError("Internal Server Error")

    def stop_streaming(self):
        video_capture.release()
        self.streaming_flag = False

