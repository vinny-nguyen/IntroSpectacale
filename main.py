import cv2 as cv
import mediapipe as mp
import time
import whisper

model = whisper.load_model("base")

def main():
    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    recording = False
    video_writer = None
    video_count = 1  # Counter for saved videos

    mp_face_detection = mp.solutions.face_detection

    with mp_face_detection.FaceDetection(
        model_selection=1, min_detection_confidence=0.5) as face_detection:

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            # Convert the BGR image to RGB.
            image = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            # To improve performance, mark the image as not writeable.
            image.flags.writeable = False
            results = face_detection.process(image)

            # Draw the face detection annotations on the image.
            image.flags.writeable = True
            image = cv.cvtColor(image, cv.COLOR_RGB2BGR)

            ih, iw, ic = image.shape

            if results.detections:
                # Find the detection with the largest bounding box area
                max_area = 0
                largest_detection = None

                for detection in results.detections:
                    bboxC = detection.location_data.relative_bounding_box
                    bbox_area = bboxC.width * iw * bboxC.height * ih
                    if bbox_area > max_area:
                        max_area = bbox_area
                        largest_detection = detection

                if largest_detection is not None:
                    detection = largest_detection

                    # Get bounding box coordinates
                    bboxC = detection.location_data.relative_bounding_box
                    bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                           int(bboxC.width * iw), int(bboxC.height * ih)

                    # Draw a rectangle around the face
                    #cv.rectangle(image, bbox, (0, 255, 0), 2)

                    # Set the box size to 200x150 pixels
                    box_width, box_height = 200, 150  # Size of the white box

                    # Position the box to the right of the head
                    x = bbox[0] + bbox[2] + 10  # 10 pixels to the right of the face bounding box
                    y = bbox[1] + int(bbox[3] / 2) - int(box_height / 2)  # Centered vertically

                    # Remove the constraints that prevent the box from exiting the frame
                    # Comment out or remove the following code:

                    # if x + box_width > iw:
                    #     x = iw - box_width - 10
                    # if y + box_height > ih:
                    #     y = ih - box_height - 10
                    # if y < 0:
                    #     y = 10

                    # Draw the white box
                    cv.rectangle(image, (x, y), (x + box_width, y + box_height), (255, 255, 255), -1)

            # Write frame to video if recording
            if recording:
                video_writer.write(image)
                cv.putText(image, 'Recording...', (10, ih - 10), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv.imshow('Head Scanner', image)

            key = cv.waitKey(1) & 0xFF
            if key == ord('q'):
                recording = not recording  # Toggle recording state

                if recording:
                    # Start recording
                    filename = f"video_{video_count}.avi"
                    fourcc = cv.VideoWriter_fourcc(*'XVID')
                    fps = 20.0
                    frame_size = (image.shape[1], image.shape[0])
                    video_writer = cv.VideoWriter(filename, fourcc, fps, frame_size)
                    print(f"Started recording: {filename}")
                else:
                    # Stop recording
                    video_writer.release()
                    print(f"Stopped recording: video_{video_count}.avi")
                    video_count += 1
                    video_writer = None


            elif key == 27:  # 'Esc' key to exit
                if recording:
                    video_writer.release()
                break

        cap.release()
        cv.destroyAllWindows()

def transcribe(audio):
    result = model.transcribe("audio.mp3")
    print(result["text"])

if __name__ == "__main__":
    main()
