import datetime
import os
import json
from flask import jsonify
import numpy as np
import cv2
import tensorflow as tf
import cvlib as cv
from cvlib.object_detection import draw_bbox
from imageai.Detection import VideoObjectDetection
import db
from bson import json_util
from flask_pymongo import PyMongo


UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
OUTPUT_FOLDER = os.path.join('staticFiles', 'output')


def detect_and_draw_box( img_filepath, model="yolo.h5", confidence=0.2):
    """Detects common objects on an image and creates a new image with bounding boxes.

    Args:
        img_filepath (str): Directory path for the uploaded image e.
        model (str): Either "yolov3" or "yolov3-tiny". Defaults to "yolov3-tiny".
        confidence (float, optional): Desired confidence level. Defaults to 0.5.
    """
    response = {}

    if img_filepath.split(".")[-1] in ("mp4", "mov", "avi"):
        print("File is a video")
        return detect_video2(img_filepath)
    else:

        img = cv2.imread(img_filepath) # Read the image into a numpy array
        bbox, label, conf = cv.detect_common_objects(img, confidence=confidence, model=model) # Perform the object detection

        print("This is the bbox, label, conf", bbox, label, conf)
        print(f"========================\nImage processed: {img_filepath}\n")  # Print current image's filename
        for l, c in zip(label, conf):
            print(f"Detected object: {l} with confidence level of {c}\n") # Print detected objects with confidence level

        output_image = draw_bbox(img, bbox, label, conf) # Create a new image that includes the bounding boxes and label
        filename = img_filepath.split("/")[-1].split(".")[0]
        output_image_path = os.path.join(OUTPUT_FOLDER,  # Specified path using the image filename
                                         'output_image_{name}.jpg'.format(name=filename))
        cv2.imwrite(output_image_path, output_image) # Save the image in the directory images_with_boxes

        response = write_response(bbox, label, conf, width = img.shape[1], height= img.shape[0])
        write_json("staticFiles/output/", "out_response_{name}.json".format(name=filename), data=response ) # Sanity Check to Save the response as a JSON locally
        add_data(response) # Add the response JSON to mongodb table

        return output_image_path, response, 'image'

def write_response(bbox, label, conf,width, height):
    response={}
    response['Bounding Box Coordinates'] = bbox
    response['Object Class'] = label
    response['Confidence'] = conf
    now = datetime.datetime.now()
    timestamp = str(now.strftime("%Y-%m-%d_%H:%M:%S"))
    response['Timestamp'] = timestamp
    response['Image Metadata'] = {'width': width, 'height': height}

    return response

def detect_video2(video_filepath):
    print("this is the video file path", video_filepath)

    filename = video_filepath.split("/")[-1].split(".")[0]
    out_path = os.path.join(OUTPUT_FOLDER, "video_result_{name}".format(name=filename))
    cap = cv2.VideoCapture(video_filepath) #Creates a video capture object, which would help stream or display the video.
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG') #Saves the output video to a directory.
    out = cv2.VideoWriter(out_path, fourcc, 10, size)
    ls=[]
    while cap.isOpened():

        ret, frame = cap.read() # Returns a tuple bool and frame, if ret is True then there's a video frame to read
        height, width, _ = frame.shape
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        frame = cv2.flip(frame, 1) # Image may endup upsidedown, flip it
        bbox, label, conf = cv.detect_common_objects(frame, confidence=0.50, model="yolo.h5")
        output_frame = draw_bbox(frame, bbox, label, conf)
        out.write(output_frame)  # Write the frame to the output files
        ls.append(output_frame)

        print("Streaming...")
        cv2.imshow('frame', output_frame)
        response = write_response(bbox, label, conf, width, height)
        k = cv2.waitKey(20)
        if k == 113: # wait.key() how long to pause between video and monitor keyboard for user input.
            # framsepress "q", 113ascii val for "q" to stop recording
            break
    #add_data(response)
    write_json("staticFiles/output/", "out_response_{name}.json".format(name=filename), data=response)
    cap.release() #Once the video stream is fully processed or the user prematurely exits the loop,
    # you release the video-capture object (vid_capture) and close the window
    out.release()
    cv2.destroyAllWindows()

    return ls[0], response,  'video'

def add_data(response):
    print("In the add data function")
    rs = json.loads(json_util.dumps(response))
    #js = jsonify(response)
    db.db.collection.insert_one(rs)

def allowed_file(filename):

    fileExtension = filename.split(".")[-1] in ("jpg", "jpeg", "png", "webp", "mp4", "mov", "avi")

    if not fileExtension:
        raise HTTPException(status_code=415, detail="Unsupported file provided.")

def write_json(target_path, target_file, data):

    #print("in the write_json function")
    with open(os.path.join(target_path, target_file), 'w') as f:
        json.dump(data, f)


def to_dynamodb():
    print("In the to_dynamodb function")
    jsonDict = json.loads("staticFiles/output/out_response.json")
    table = dynamodb.Table('aizatron-app')
    for item in jsonDict:
        table.put_item(Item=item)