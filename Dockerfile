FROM python:bullseye

RUN mkdir "docker_app"
WORKDIR "docker_app"

RUN apt update
RUN apt install git -y
RUN apt install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
RUN pip install gunicorn
RUN git clone https://github.com/eclerchig/CalcMedian_Project.git
WORKDIR "CalcMedian_Project"
RUN pip install -r requirements.txt
ARG WORKER_ENV=3
ENV WORKER_ENV="${WORKER_ENV}"
CMD ["sh", "-c", "gunicorn --bind :8111 --workers $WORKER_ENV main:server"]