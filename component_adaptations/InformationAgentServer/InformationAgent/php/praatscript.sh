#!/bin/bash

echo praat $* > /tmp/xx
echo praat $* > /tmp/log
#/usr/bin/praat $*
praat getFeatPraat2arg.praat /tmp/uploaded_audio.wav /tmp/p.feat
date  >> /tmp/log
