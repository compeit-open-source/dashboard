#!/bin/sh

cd ../..
tar cvfz docker-build/dashboard/dashboard.tar.gz app config.py manage.py tests
cd docker-build/dashboard
cp -p ../../requirements.txt .

docker build -t test/dashboard .