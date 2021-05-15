FROM python:3.9.1

LABEL "version"="0.0.1"
LABEL "repository"="https://github.com/yhkl-dev/ADSyncToAliyun"
LABEL "maintainer"="yhkl"
LABEL "description"="ad account sync to aliyun"

RUN mkdir /app
COPY . /app
RUN pip install -r /app/requirements.txt -i https://pypi.douban.com/simple
WORKDIR /app

CMD ["python","main.py"]