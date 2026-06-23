#!/usr/bin/env bash

# delete old data 
echo "----Deleting old data...--------"

rm -rf data/sports_news/*
rm -rf data/entertaining/*
rm -rf data/educational/*

echo "------Old data deleted. ------"

echo "----Importing raw data from the internet..."

python3 data_creation.py

echo "------Raw data imported. ------"

echo "----Creating dataset from raw data... -----"

python3 populate_dataset.py

echo "------Dataset created. ------"
