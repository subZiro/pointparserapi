#!/bin/sh

flask deploy
exec gunicorn -b :5000 --access-logfile - --error-logfile - main:app --timeout 180
