FROM python:bullseye

RUN mkdir "docker_app"
WORKDIR "docker_app"

RUN apt update
RUN apt install git -y
RUN apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
RUN pip install gunicorn
RUN git clone https://github.com/eclerchig/CalcMedian_Project.git && cd CalcMedian_Project && git checkout fix_app_in_docker
WORKDIR "CalcMedian_Project"
RUN pip install -r requirements.txt
RUN pip install scipy==1.10.0
ARG WORKER_ENV=3
ENV WORKER_ENV="${WORKER_ENV}"
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8000 --workers $WORKER_ENV main:server"]