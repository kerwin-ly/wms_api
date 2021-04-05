FROM python:3.7.4
MAINTAINER kerwin
RUN mkdir -p /project/wms_api
WORKDIR /project/wms_api
COPY requirements.txt /project/wms_api/
#install requires
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
ADD . /project/wms_api
#CMD ["sh", "./scripts/start.sh"]