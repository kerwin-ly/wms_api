#!/usr/bin/env bash
SCRIPTS_DIR=$(cd `dirname $0`; pwd)
PROJECT_DIR=$(cd $(dirname ${SCRIPTS_DIR}); pwd)
cd "${PROJECT_DIR}"
pwd

export PYTHONPATH=$(pwd)
export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_DEBUG=1


flask db migrate && flask db upgrade

if [ "$?" != "0" ]; then
    echo "An error occurred when flask db migrate or upgrade"
    exit 1
fi

gunicorn -w 1 -b 0.0.0.0:5000 \
--threads 4 \
--access-logfile logs/gun-access.log \
--error-logfile logs/gun-error.log \
--access-logformat '%(t)s %(h)s %(U)s %(m)s %(s)s %(T)s' \
main:app



