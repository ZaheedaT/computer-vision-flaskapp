from IPython.display import Image, display
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
import PIL.Image
from PIL.ExifTags import TAGS
import decimal
import db
import logging
import pprint
import boto3
from botocore.exceptions import ClientError
from bson import json_util
from flask_pymongo import PyMongo

logger = logging.getLogger(__name__)
#from pprint import pprint

dyn_resource = boto3.resource('dynamodb')

UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
OUTPUT_FOLDER = os.path.join('staticFiles', 'output')


def store_result(path_name_ = "boxed_images"):
    if not os.path.exists(path_name_): # check if the dir exists, create one if not
        os.mkdir(path_name_)
        
    return "Created Boxed Images Directory"
        
def detect_and_draw_box( img_filepath, model="yolo.h5", confidence=0.2):
    """Detects common objects on an image and creates a new image with bounding boxes.

    Args:
        img_filepath (str): Directory path for the uploaded image e.
        model (str): Either "yolov3" or "yolov3-tiny". Defaults to "yolov3-tiny".
        confidence (float, optional): Desired confidence level. Defaults to 0.5.
    """
    response = {}
    ls = []

    if img_filepath.split(".")[-1] in ("mp4", "mov", "avi"):
        print("File is a video")
        return detect_video2(img_filepath)
    else:
        # Read the image into a numpy array
        img = cv2.imread(img_filepath)

        # Perform the object detection
        bbox, label, conf = cv.detect_common_objects(img, confidence=confidence, model=model)

        print("This is the bbox, label, conf", bbox, label, conf)
        # Print current image's filename
        print(f"========================\nImage processed: {img_filepath}\n")

        # Print detected objects with confidence level
        for l, c in zip(label, conf):
            print(f"Detected object: {l} with confidence level of {c}\n")

        # Create a new image that includes the bounding boxes
        output_image = draw_bbox(img, bbox, label, conf)
        filename = img_filepath.split("/")[-1].split(".")[0]
        output_image_path = os.path.join(OUTPUT_FOLDER, 'output_image_{name}.jpg'.format(name=filename))
        ls.append(output_image_path)
        # Save the image in the directory images_with_boxes
        cv2.imwrite(output_image_path, output_image)

        response['Bounding Box Coordinates'] = bbox
        response['Object Class'] =  label
        response['Confidence'] =  conf
        now = datetime.datetime.now()
        timestamp = str(now.strftime("%Y-%m-%d_%H:%M:%S"))
        response['Timestamp'] = timestamp
        response['Image Metadata'] = {'width':  img.shape[1] , 'height':img.shape[0]}
        # responser = {
        #     "aizatron-app": [  {
        #       "PutRequest":response}]  } # AWS DynamoDB


        filename = img_filepath.split("/")[-1].split(".")[0]

        write_json("staticFiles/output/", "out_response_{name}.json".format(name=filename), data=response )
        add_data(response)

        return output_image_path, response, 'image'


def detect_video2(video_filepath):
    print("this is the video file pathh", video_filepath)
    response ={}
    filename = video_filepath.split("/")[-1].split(".")[0]
    out_path = os.path.join(UPLOAD_FOLDER, "video_result_{name}".format(name=filename))
    cap = cv2.VideoCapture(video_filepath) #Creates a video capture object, which would help stream or display the video.
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') #Saves the output video to a directory.
    out = cv2.VideoWriter(out_path, fourcc, 15, (640, 480))


    while cap.isOpened():
        # vid_capture.read() methods returns a tuple, first element is a bool
        22
        # and the second is frame

        ret, frame = cap.read() # if ret is True then there's a video frame to read
        height, width, _ = frame.shape
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        frame = cv2.flip(frame, 1)
        #cv2.rectangle(frame, (100, 100), (500, 500), (0, 255, 0), -1)
        out.write(frame) ## Write the frame to the output files
        cv2.imshow('frame', frame)
        bbox, label, conf = cv.detect_common_objects(frame, confidence=0.50, model="yolo.h5")
        now = datetime.datetime.now()
        timestamp = str(now.strftime("%Y-%m-%d_%H:%M:%S"))
        print("Adding data to JSON")
        response['Timestamp'] = timestamp
        response['Object Class'] = label
        response['Bounding Box Coordinates'] = bbox
        response['Confidence'] = conf
        print("Done Adding data to json, about to add data to MongoDB")
        k = cv2.waitKey(20)
        if k == 113: # wait.key() how long to pause between video and monitor keyboard for user input.
            # framsepress "q", 113ascii val for "q" to stop recording
            break
        else:
            break
    add_data(response)
    filename = video_filepath.split("/")[-1].split(".")[0]
    write_json("staticFiles/output/", "out_response_{name}.json".format(name=filename), data=response)
    cap.release() #Once the video stream is fully processed or the user prematurely exits the loop,
    # you release the video-capture object (vid_capture) and close the window
    out.release()
    cv2.destroyAllWindows()

    return video_filepath , response,  'video'

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