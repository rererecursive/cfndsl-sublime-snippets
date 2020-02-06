#!/bin/sh
VERSION=$(gem query --local --exact --no-verbose cfndsl | egrep -o "(\d|\.)+")
cp /usr/local/bundle/gems/cfndsl-$VERSION/lib/cfndsl/aws/resource_specification.json /app
#cat /app/resource_specification.json
python3 main.py
