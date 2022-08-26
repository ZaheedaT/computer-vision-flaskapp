# Aizatron - Take Home Assignment

Build a Flask API that can be used to detect objects, display the ROIs along with class names from
images provided through an endpoint.
Your web application should allow a user to upload a file (you can use postman) and perform object
detection to it. The model will be deployed in a Flask Framework environment in Python.

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
* Jinja2==3.1.2
* opencv-python==4.6.0.66
* nest-asyncio==1.5.5
* tensorflow==2.9.1
* imageai==2.1.6
* boto3==1.24.57
* pymongo==4.2.0


#### App Installation
1. Clone the repo:
```shell
git clone https://gitlab.com/zaheedatshankie1/computer-vision-flaskapp.git
```
3. Run the setup file which installs:
* python3-pip
* creates a Venv Virtual Environment 

```sh 
sh setup.sh
```
4. Activate Virtual Environment
```shell
source aizatron_env/bin/activate
```
5. Install dependencies

Download yolo.h5

`wget https://github.com/OlafenwaMoses/ImageAI/releases/download/1.0/yolo.h5`

Tensorflow Installation 

`python3 -m pip install tensorflow`

```shell
pip3 install -r requirements.txt
```

#### Run the App
```sh
flask run
```
Exit the app using keyboard shortcuts:
`ctrl + c`

#### App Workflow
The app allows the user to upload an image or a video.
Upon uploading, the user will be taken to an endpoint to view the image/video, the user then clicks `detect object` , a new endpoint will appear with a picture of the Output as well as a display of the Response dictionary. 
The results of the image/video uploaded will be saved in Mongodb Atlas database with the following fields:

Database fields:
1. Timestamp
2. Object class
3. Bounding box coordinates
4. Confidence
5. Image metadata 
6. Any additional features 

Ideally the data would not be stored in the Repo, by using an Argument Parser when running the app we can specify a link/path to the data. Or use DVC to pull different data versions. 


#### Mongodb Atlas
Login to view database

### Improvements 
Improvements I could make are App/Unit tests, and better documentation under function definitions. It was my first time using a NoSQL framework and I've managed to use learn and implement MongoDB. I had a good try at using AWS DynamoDB , with a bit more learning and time I can make that aspect work. 



