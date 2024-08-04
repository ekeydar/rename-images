# base image  
FROM python:3.11   

# setup environment variable  
ENV scriptsDir=/home/app  

# set work directory  
RUN mkdir -p $scriptsDir  

# where your code lives  
WORKDIR $scriptsDir  

# set environment variables  
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

# install packages
RUN apt-get update 

# install dependencies  
RUN pip install --upgrade pip

RUN git clone https://github.com/exiftool/exiftool.git

ENV workDir=/home/images

RUN mkdir -p $workDir

COPY ./rename_images_in_folder.py $scriptsDir

RUN chmod +x ./rename_images_in_folder.py

ENV PATH="$PATH:${scriptsDir}:${scriptsDir}/exiftool"

WORKDIR $workDir

# to run the docker file
# docker run -d -p 8000:8000 -v $(pwd):/home/app/webapp ekeydar/django-tut:1 sh -c ./scripts/init_docker.sh

ENTRYPOINT ["sh", "-c", "rename_images_in_folder.py \"$@\"", "--"]

# To build
# docker build . -t ekeydar/rename-images-in-folder
# To run
# replaces /Users/eran/Paris with the images folder
# docker run -v /Users/eran/Paris:/home/images ekeydar/rename-images-in-folder
