import datetime
import os
import json
import numpy as np
import cv2
import cvlib as cv
from cvlib.object_detection import draw_bbox
from imageai.Detection import VideoObjectDetection
from bson import json_util
from flask_pymongo import PyMongo
from flask import current_app as app

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf


UPLOAD_FOLDER = os.path.join('static', 'uploads')
OUTPUT_FOLDER = os.path.join('static', 'output')



def detect_and_draw_box( img_filepath: str, model="yolo.h5", confidence=0.2):
    """Detects common objects on an image and creates a new image with bounding boxes and a Class Label.

    Parameters:
        img_filepath (str): Directory path for the uploaded image e.
        model (str): Either "yolov3" or "yolov3-tiny". Defaults to "yolov3-tiny".
        confidence (float, optional): Desired confidence level. Defaults to 0.5.
    Returns:
        output_image_path (str):
        response (dict): A dictionary containing response data from the model's results.
        filetype (str): A string stating that the filetype is a video.

    """

    if img_filepath.split(".")[-1] in ("mp4", "mov", "avi"):
        print("\nFile is a video")
        return detect_video(img_filepath, confidence, model)
    else:
        print("\nFile is an image")
        img = cv2.imread(img_filepath) # Read the image into a numpy array
        bbox, label, conf = cv.detect_common_objects(img, confidence=confidence, model=model) # Perform the object detection


        for l, c in zip(label, conf):
            print(f"Detected object: {l} with confidence level of {c}\n") # Print detected objects with confidence level

        output_image = draw_bbox(img, bbox, label, conf) # Create a new image that includes the bounding boxes and label

        filename = img_filepath.split("/")[-1].split(".")[0]
        output_image_path = os.path.join(OUTPUT_FOLDER,  # Specified path using the image filename
                                         'output_image_{name}.jpg'.format(name=filename))
        print(f"========================\nImage processed: {output_image_path}\n")  # Print current image's filename

        cv2.imwrite(output_image_path, output_image) # Save the image in the directory images_with_boxes

        response = write_response(bbox, label, conf, width = img.shape[1], height= img.shape[0])
        write_json(OUTPUT_FOLDER, "out_response_{name}.json".format(name=filename), data=response ) # Sanity Check to Save the response as a JSON locally
        #add_data(response) # Add the response JSON to mongodb table
        filetype = 'image'
        return output_image_path, response, filetype


def detect_video(video_filepath, confidence:float, model=str):
    """Performs Object Detection on an uploaded video. It adds the Boundary Boxes as well as a label to the video as it streams.

    Parameters:
        video_filepath (str): The path of the video uploaded by the user.
    Returns:
            response (dict): A dictionary containing response data from the model's result.
            filetype (str): A string stating that the filetype is a video.
    """

    print("\nPerforming Video Object Detection...")


    filename = video_filepath.split("/")[-1].split(".")[0]
    out_path = os.path.join(OUTPUT_FOLDER, "video_result_{name}".format(name=filename))
    cap = cv2.VideoCapture(video_filepath) #Creates a video capture object, which would help stream or display the video.
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (width, height)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG') #Saves the output video to a directory.
    fps = int(round(cap.get(5)))
    #print("\nThis is the fps", fps)
    #out = cv2.VideoWriter(out_path, fourcc, 10.0, size)

    response =dict()
    #ls=[]
    while cap.isOpened():

        ret, frame = cap.read() # Returns a tuple bool and frame, if ret is True then there's a video frame to read
        height, width, _ = frame.shape
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        frame = cv2.flip(frame, 1) # Image may end up upsidedown, flip it
        bbox, label, conf = cv.detect_common_objects(frame, confidence=confidence, model=model)
        output_frame = draw_bbox(frame, bbox, label, conf)
        out = cv2.VideoWriter(out_path, fourcc, 10.0, (640, 480))
        out.write(output_frame)  # Write the frame to the output files

        print("Streaming...")
        cv2.imshow('frame', output_frame)
        response['response'] = (write_response(bbox, label, conf, width, height))
        k = cv2.waitKey(20)
        if k == 113: # wait.key() how long to pause between video and monitor keyboard for user input.
            # framsepress "q", 113ascii val for "q" to stop recording
            break
    #add_data(response)
    cap.release() #Once the video stream is fully processed or the user prematurely exits the loop,
    out.release()   #You release the video-capture object (vid_capture) and close the window
    cv2.destroyAllWindows()
    write_json(OUTPUT_FOLDER, "out_response_{name}.json".format(name=filename), data=response)
    filetype = 'video'

    return video_filepath, response['response'],  filetype

def add_data(response):
    """Adds data into MongoDB Atlas (NoSQL). It takes a python dict and converts it into JSON format first.

    Parameters:
     response (dict): A JSON-like object that has response data from our model
    """

    print("\nAdding data to MongoDB Atlas...")
    rs = json.loads(json_util.dumps(response))
    db.db.collection.insert_one(rs)

def allowed_file(filename):
    """A function that checks whether the uploaded filetype is allowed using its extension.
    Supported file types: "jpg", "jpeg", "png", "webp", "mp4", "mov", "avi".

    Parameters:
        filename (str): The name of the uploaded file, including its extension.
    Raises:
        An exception if the filetype is not allowed.
    """

    file_extension = filename.split(".")[-1] in ("jpg", "jpeg", "png", "webp", "mp4", "mov", "avi")

    if not file_extension:
        raise HTTPException(status_code=415, detail="Unsupported file provided.")

def write_response(bbox, label, conf,width, height):
    """ Adds model results to a dictionary to create a response object

    Parameters:
        bbox (list):
        label (list of str):
        conf (list of float):
        width (float):
        height  (float):

    Returns:
        response (dict): A dictionary containing response data from the model's results.

    """
    response= dict()
    response['Bounding Box Coordinates'] = bbox
    response['Object Class'] = label
    response['Confidence'] = conf
    now = datetime.datetime.now()
    timestamp = str(now.strftime("%Y-%m-%d_%H:%M:%S"))
    response['Timestamp'] = timestamp
    response['Image Metadata'] = {'width': width, 'height': height}

    return response

def write_json(target_path, target_file, data):

    with open(os.path.join(target_path, target_file), 'w') as f:
        json.dump(data, f)

