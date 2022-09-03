# Computer Vision WebApp using Flask, OpenCV and MongoDB

The app allows for the user to upload an image or video, perform object detection on the uploaded file and output results to MongoDB.
* How to build the WebApp detailed instructions - https://medium.com/@zaheedatshankie/build-a-computer-vision-webapp-flask-opencv-and-mongodb-62a52d38738a

### Project Structure
```shell

├── app.py       # contains the Flask app object
├── utils.py
├── db.py
└── setup/
│       ├── requirements.txt
│       ├── setup.sh 
└── staticFiles/
│     ├── images # Images to use to test the App
│     ├── videos # Videos to test the App
│     ├── output # Output JSON and images stored here
│     ├── uploads # User uploads saved here
└── templateFiles /
│    ├── index.html
│    ├── show_image.html
│    ├── show_video.htl
│    ├── success.html# unit tests
└── tests/
│   ├── conftest.py  # Test cfg
│   └── test_app.py  # unit tests
└── README.md
```



#### Prerequisites
* Flask==2.1.0
* pandas==1.4.0
* numpy==1.23.2
* Jinja2==3.1.2
* opencv-python==4.6.0.66
* nest-asyncio==1.5.5
* imageai==2.1.6
* pymongo==4.2.0


#### App Installation
##### 1. Clone the repo:
```shell
git clone https://github.com/ZaheedaT/computer-vision-flaskapp.git
```
##### 2. Run the setup file which installs:
* python3-pip
* creates a Venv Virtual Environment 

```sh 
sh setup.sh
```
##### 3. Activate Virtual Environment
```shell
source flaskapp_env/bin/activate
```
##### 4. Install dependencies

<ins>Download yolo.h5</ins>

`wget https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5`

<ins>Tensorflow Installation</ins>

`python3 -m pip install tensorflow`

```shell
pip3 install -r requirements.txt
```
##### 5. Set Basic Environment Variables
```
export FLASK_APP= app.py
export FLASK_ENV=development
```

## Run the App
```sh
python3 app.py
```
Exit the app using keyboard shortcuts:
`ctrl + c`

#### App Workflow
The app allows the user to upload an image or a video.
Upon uploading, the user will be taken to an endpoint to view the image/video, the user then clicks "detect object" , a new endpoint will appear with a picture of the Output. The results of the image/video uploaded will be saved locally in JSON format and in a Mongodb Atlas database with the following fields:

Database fields:
1. Timestamp
2. Object class
3. Bounding box coordinates
4. Confidence
5. Image metadata 


#### Mongodb Atlas
Follow instructions on https://medium.com/@zaheedatshankie/build-a-computer-vision-webapp-flask-opencv-and-mongodb-62a52d38738a

### Improvements 
Add App/Unit tests. Ideally the data would not be stored in the Repo, by using an Argument Parser when running the app we can specify a link/path to the data. Or use DVC to pull different data versions. 

** Credit for css designs: https://github.com/OmdenaAI/omdena-ghana-creditworthiness/tree/main/original/flask_app



