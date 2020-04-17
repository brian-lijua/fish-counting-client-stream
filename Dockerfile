FROM balenalib/raspberrypi3-debian
WORKDIR /home/app
RUN apt update && apt install -y \
  python3.7 \
  python3-pip \
  python3-numpy \  
  ffmpeg  \
  python3-opencv \
  libraspberrypi-bin
COPY requirements-docker.txt /home/app/requirements.txt
COPY fish_counter_web_stream ./server
RUN pip3 install -r requirements.txt
CMD [ "python3", "server/main.py" ]