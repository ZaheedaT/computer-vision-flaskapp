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
import boto3
#from pprint import pprint



UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')


def store_result(path_name_ = "boxed_images"):
    if not os.path.exists(path_name_): # check if the dir exists, create one if not
        os.mkdir(path_name_)
        
    return "Created Boxed Images Directory"
        
def detect_and_draw_box( img_filepath, model="yolov3-tiny", confidence=0.2):
    """Detects common objects on an image and creates a new image with bounding boxes.

    Args:
        filename (str): Filename of the image.
        model (str): Either "yolov3" or "yolov3-tiny". Defaults to "yolov3-tiny".
        confidence (float, optional): Desired confidence level. Defaults to 0.5.
    """
    response = {}
    ls = []
    count = 0
    if img_filepath.split(".")[-1] in ("mp4", "mov"):
        detect_video2(img_filepath)
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
        # org

        output_image_path = os.path.join(UPLOAD_FOLDER, 'output_image.jpg')
        ls.append(output_image_path)
        # Save the image in the directory images_with_boxes
        cv2.imwrite(output_image_path, output_image)
        # image = PIL.Image.open(img_filepath)
        #
        # # Get the exif data and map to the correct tags
        # exif_data = {
        #     PIL.ExifTags.TAGS[k]: v
        #     for k, v in image._getexif().items()
        #     if k in PIL.ExifTags.TAGS
        # }

        # Display the image with bounding boxes
        #display(Image(f'images_with_boxes/{filename}')) # Use this display on the screen or as a saved picture
        response['Bounding Box Coordinates'] = {"L": bbox}
        response['Object Class'] = {"L" : label}
        response['Confidence'] = {"L" : conf}
        now = datetime.datetime.now()
        timestamp = str(now.strftime("%Y-%m-%d_%H:%M:%S"))
        response['Timestamp'] = {"S": timestamp}
        response['Image Metadata'] = {"M": {'width': {"N": img.shape[1]} , 'height': {"N": img.shape[0]} }}
        # responser = {
        #     "aizatron-app": [  {
        #         "PutRequest":response}]  }




        open("staticFiles/output/out_response.json", "w").write(json.dumps(response))

        # jsonify(json.dump(response))

        return ls, response, 'image'
    return detect_video2(img_filepath)

def to_dynamodb():
    jsonDict = json.loads("staticFiles/output/out_response.json")
    table = dynamodb.Table('aizatron-app1')
    for item in jsonDict:
        table.put_item(Item=item)

def detect_video(video_filepath):
    ls =[]
    response = {}
    execution_path = os.getcwd()

    camera = cv2.VideoCapture(0)

    detector = VideoObjectDetection()
    detector.setModelTypeAsYOLOv3()
    detector.setModelPath(os.path.join(execution_path, "yolo.h5"))
    detector.loadModel()
    video_path = detector.detectObjectsFromVideo(camera_input=camera,
                                                 output_file_path=os.path.join(execution_path, "camera_detected_video")
                                                 , frames_per_second=20,
                                                 log_progress=True,
                                                 return_detected_frame=True,
                                                 minimum_percentage_probability=30)

    bbox, label, conf = cv.detect_common_objects(frame, confidence=0.25, model="yolo.h5")

    print(bbox, label, conf)
    ls.append(video_path)
    print("This is the video path", ls)
    return ls, response
# Read in image from POST request

def detect_video2(video_filepath):
    response ={}
    execution_path = os.getcwd()
    cap = cv2.VideoCapture(video_filepath)
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(os.path.join(execution_path, "video_result"), fourcc, 15, (640, 480))
    #count=0
    while cap.isOpened():

        ret, frame = cap.read()


        #print(bbox, label, conf)
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        frame = cv2.flip(frame, 1)
        # write the flipped frame
        out.write(frame)
        cv2.imshow('frame', frame)
        bbox, label, conf = cv.detect_common_objects(frame, confidence=0.50, model="yolo.h5")
        open("out_response_video.json", "w").write(json.dumps(response))
        now = datetime.datetime.now()
        timestamp = str(now.strftime("%Y-%m-%d_%H:%M:%S"))
        response['Timestamp'] = timestamp
        response['Object Class'] = label
        response['Bounding Box Coordinates'] = bbox
        response['Confidence'] = conf

        if cv2.waitKey(1) == ord('q'):
            break
    # Release everything if job is finished

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    return [os.path.join(execution_path, "video_result")] , response,  'video'





def read_data(image_file_, dir_name_ = "uploaded_images"):
    """"Will read in the uploaded imageand put  
    results in the boxed_image directory"""
    
    if not os.path.exists(dir_name_): # Create Directory for the uploaded staticFiles
        os.mkdir(dir_name_)
    
    detect_and_draw_box(image_file) # Create object Detection on image
    
    return render_template('show_image.html', user_image = dir_name_)

