import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
import time
import cv2
import PIL as Image

# solenoid opens when 12V applied at 0.3A

#gives the camera attributes
def getDataAttributes():
    dataIndex = open("./dataIndex.txt", "r")
    last_file_number = dataIndex.readline().split()[1]
    last_file_number = int(last_file_number)
    
    interval_in_seconds = dataIndex.readline().split()[1]
    interval_in_seconds = int(interval_in_seconds)
    
    prefix = dataIndex.readline().split()[1]
    
    dataIndex.close()
    return [last_file_number, interval_in_seconds, prefix]

# sets attributes in dataindex.txt file
def setAttributes(attributes):
    dataIndex = open("./dataIndex.txt", "w")
    dataIndex.writelines(["last_file_number: " + str(attributes[0]), '\n',
                          "interval_in_seconds: " + str(attributes[1]), '\n',
                          "file_name_prefix: " + attributes[2]])
    dataIndex.close()

#input camera attributes and capture image, updates attributes and returns new attributes
def cameraCapture(attributes):
    picam2 = Picamera2()
    camera_config = picam2.create_still_configuration()
    picam2.start()
    name = "../images/" + attributes[2] + (str(attributes[0] + 1)) + ".jpg"
    picam2.capture_file(name)
    attributes[0] += 1
    setAttributes(attributes)
    picam2.close()
    return attributes

def lastFileName():
    attributes = getDataAttributes()
    if (attributes[0] == 0):
        return "placeholder.jpg"
    return "../images/" + attributes[2] + str(attributes[0]) + ".jpg"

def create_video(image_paths, output_video_path, fps=24, size=None):
    if not image_paths:
        raise ValueError("The list of image paths is empty")
    print(":IORHGUIGHUBHSULIGH")
    print(image_paths[0])
    first_frame = cv2.imread(image_paths[0])
    if first_frame is None:
        raise ValueError("Cannot read image at path")
    
    if size is None:
        height, width, _ = first_frame.shape
        size = (width, height)
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, size)
    
    for path in image_paths:
        frame = cv2.imread(path)
        if frame is None:
            print(f"Warning: Could not read {path}, skipping.")
            continue
        frame_resized = cv2.resize(frame, size)
        out.write(frame_resized)
        
    out.release()
    print(f"Vido saved to {output_video_path}")

