FROM nvcr.io/nvidia/pytorch:23.05-py3

RUN apt-get update
# Needed for fury vtk. ffmpeg also needed
RUN apt-get install ffmpeg libsm6 libxext6 -y
RUN apt-get install xvfb -y

RUN pip install --upgrade pip

# installing pyradiomics results in an error in github actions
# RUN pip pyradiomics

COPY . /app
RUN pip install /app
RUN pip install flask flask_cors
RUN pip install git+https://github.com/wasserth/TotalSegmentator.git
# RUN python /app/totalsegmentator/download_pretrained_weights.py

RUN cd /app
WORKDIR /app
ENV FLASK_APP=App.py
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
# expose not needed if using -p
# If using only expose and not -p then will not work
# EXPOSE 80
