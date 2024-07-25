# Parent Image
# FROM nvcr.io/nvidia/pytorch:20.10-py3
FROM nvcr.io/nvidia/pytorch:23.05-py3

ENV nnUNet_raw_data_base "/home/nnUNet/data/nnUNet_raw_data_base"
ENV nnUNet_preprocessed "/home/nnUNet/data/nnUNet_preprocessed"
ENV nnUNet_results "/home/nnUNet/data/models"
ENV RESULTS_FOLDER "/home/nnUNet/data/modelsv1"

RUN mkdir -p /home/models

COPY App.py /home
COPY data_utils.py /home
COPY Pancreas.py /home

RUN mkdir -p /home/templates
COPY templates/*.html /home/templates/

RUN mkdir -p /home/nnUNet && \
    pip install nnunetv2==2.2.1 && \
    pip install TotalSegmentator && \
    pip install nnunet && \
    pip install flask && \
    pip install git+https://github.com/radreports/blast-ct-vip.git && \
    pip install tensorboard && \
    mkdir -p /home/nnUNet/input && \
    mkdir -p /home/nnUNet/output && \
    mkdir -p /home/nnUNet/data && \
    mkdir -p /home/nnUNet/data/models && \
    mkdir -p /home/nnUNet/data/modelsv1 && \
    mkdir -p /home/nnUNet/data/nnUNet_raw_data_base && \
    mkdir -p /home/nnUNet/data/nnUNet_preprocessed

RUN pip install flask_cors

WORKDIR /home
ENV FLASK_APP=App.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
