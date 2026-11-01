# Lab: experiments that need a free GPU or the open internet

Runs on GitHub Actions ("Lab (Kaggle GPU)" workflow) and sends a job to the owner's free Kaggle GPU
(KAGGLE_USERNAME + KAGGLE_API_TOKEN secrets, 30 GPU hours a week). Each lab is a folder in lab/kaggle/<name>/
with a lab.py; whatever it writes to /kaggle/working/out is published as a GitHub pre-release
"lab-<name>-run<N>" so it can be inspected frame by frame against the benchmark.
Nothing here is part of the video pipeline until a test proves itself.
