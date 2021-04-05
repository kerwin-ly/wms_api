REPO=kerwinleeyi/wms_api
DEV_TAG="dev"
TIME_NOW=`date '+%Y%m%d.%H%M%S'`
TAG=$DEV_TAG.$TIME_NOW
pipenv lock -r > requirements.txt
docker build --no-cache -t $REPO:$TAG -f docker/Dockerfile .
docker push $REPO:$TAG