#!/bin/sh
echo "HUEY CONSUMER"
echo "-------------"
echo "In another terminal, run 'python3 commands'"
echo "Stop the consumer using Ctrl+C"
PYTHONPATH=".:$PYTHONPATH"
export PYTHONPATH
WORKER_CLASS=${1:-thread}
huey_consumer.py idbc.huey --workers=4 -k $WORKER_CLASS -C -S