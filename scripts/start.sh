#!/usr/bin/env bash
echo 'start gunicorn'
SCRIPTS_DIR=$(cd `dirname $0`; pwd)
PROJECT_DIR=$(cd $(dirname ${SCRIPTS_DIR}); pwd)
cd "${PROJECT_DIR}"
pwd

export PYTHONPATH=$(pwd)
export FLASK_APP=main.py
export FLASK_ENV=production
export FLASK_DEBUG=0

#flask db migrate && flask db upgrade

gunicorn main:app -c gunicorn.conf.py --reload
