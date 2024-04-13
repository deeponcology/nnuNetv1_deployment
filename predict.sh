#!/bin/bash
rm -f /home/output/*

nnUNet_predict -i $inputDir -o $outDir --task_name $1 --model 2d --disable_tta
