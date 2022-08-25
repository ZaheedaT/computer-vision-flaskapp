#!/bin/bash
# setup.sh
# a bash script to setup the environment for the project

# install pip3
sudo apt-get install python3-pip

# create the virutual environment in the project root
python3 -m venv aizatron_env
# activate the virtual environment 
source aizatron_env2/bin/activate

