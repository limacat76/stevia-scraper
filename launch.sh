#!/bin/bash
set -a 
. $HOME/.py_secrets
set +a

#if [ -z "$1" ]; then
#    REDDIT_SUBREDDIT=$1
#fi

cd $(dirname $(realpath $0))

./launch.py
