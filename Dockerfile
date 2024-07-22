# Parent Image
# FROM nvcr.io/nvidia/pytorch:20.10-py3
FROM nvcr.io/nvidia/pytorch:23.05-py3

ENV nnUNet_raw_data_base "/home/nnUNet/data/nnUNet_raw_data_base"
ENV nnUNet_preprocessed "/home/nnUNet/data/nnUNet_preprocessed"
ENV nnUNet_results "/home/nnUNet/data/models"
ENV RESULTS_FOLDER "/home/nnUNet/data/modelsv1"
RUN mkdir /home/models
# RUN wget  -O /home/models/Task055_SegTHOR.zip https://www.dropbox.com/s/m7es2ojn8h0ybhv/Task055_SegTHOR.zip?dl=0
#-O $output_path $seg_model_url
# RUN mkdir /home/models

# COPY listdir.py /home
COPY App.py /home
COPY data_utils.py /home
COPY Pancreas.py /home

RUN mkdir /home/templates
# COPY templates/upload.html /home/templates

COPY templates/*.html /home/templates/
RUN cd /home && \
  #mkdir /home/input && \
  #mkdir /home/output && \
  mkdir /home/nnUNet && \
#   pip3 install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu113 && \
  # pip install nnunet && \
  pip install nnunetv2==2.2.1 && \
  pip install nnunet && \
  pip install flask && \
  pip install git+https://github.com/biomedia-mira/blast-ct.git && \
  pip install tensorboard && \
  #git clone https://github.com/MIC-DKFZ/nnUNet.git  && \
  mkdir /home/nnUNet/input && \
#   mkdir /home/models && \
  mkdir /home/nnUNet/output && \
  mkdir /home/nnUNet/data && \
  mkdir /home/nnUNet/data/models && \
  mkdir /home/nnUNet/data/modelsv1 && \
  mkdir /home/nnUNet/data/nnUNet_raw_data_base && \
  mkdir /home/nnUNet/data/nnUNet_preprocessed && \
  cd /home/nnUNet && \
  cd /home

RUN SITE_PKG=`pip3 show nnunet | grep "Location:" | awk '{print $2}'` && \
   cp nnUNetTrainerV2_Loss_CE_checkpoints.py "$SITE_PKG/nnunet/training/network_training/nnUNetTrainerV2_Loss_CE_checkpoints.py"

RUN pip install flask_cors
# RUN chmod +x /home/pipeline.sh
# RUN chmod +x /home/predict.sh
RUN cd /home
WORKDIR /home
ENV FLASK_APP=App.py
# RUN  /home/pipeline.sh 
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
# ENTRYPOINT ["/home/pipeline.sh"]
# Installing additional libraries
# WORKDIR /workspace/
# RUN pip3 install --upgrade git+https://github.com/nanohanno/hiddenlayer.git@bugfix/get_trace_graph#egg=hiddenlayer
# RUN pip3 install progress
# RUN pip3 install graphviz

# Setting up User on Image
# Match UID to be same as the one on host machine, run command 'id'
# RUN useradd -u 3333454 -m aberg
# RUN chown -R aberg:aberg nnUNet/
# USER aberg

# Git Credentials
# RUN git config --global user.name "abergsneider"
# RUN git config --global user.email "andresbergsneider@gmail.com"
