#!/usr/bin/env bash


cd ~/ShotMat.Wk/shotmat/api
rm -rf .venv
python3.12 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r shotmat_api/requirements.txt
