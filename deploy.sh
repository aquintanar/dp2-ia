#!/bin/bash

git switch main
git fetch
git reset --hard origin/main

# Check if a parameter is provided
if [ -z "$1" ]; then
  echo "Debe introducir la direccion url base, por ejemplo: $0 http://3.218.68.113"
  exit 1
fi

# Assign the parameter to a variable
PARAMETER=$1
processed_url="${PARAMETER#*//}"

# Use the parameter
echo "The parameter provided is: $PARAMETER"

# Example of using the parameter in a command
sed -i "s|http://localhost:3000|$PARAMETER/api|g" IA-Angel/app/model/model.py

cd IA-Angel/app/
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
