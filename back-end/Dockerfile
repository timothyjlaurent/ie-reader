# Use an official Python runtime as a parent image
#FROM python:3.7.2-slim
FROM python:3

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

# install spacy language model
#RUN python -m spacy download en_core_web_sm
RUN mkdir model

RUN wget -P model https://s3-us-west-2.amazonaws.com/allennlp/models/coref-model-2018.02.05.tar.gz

RUN wget -P model https://s3-us-west-2.amazonaws.com/allennlp/models/openie-model.2018-08-20.tar.gz

RUN pip install  http://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz \
  --trusted-host github-production-release-asset-2e65be.s3.amazonaws.com -v

COPY src src

# Run server.py when the container launches
CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--workers=1", "--worker-class", "gevent", "--timeout", "1600", "--pythonpath", "./src", "ie_reader.app:app" ]
