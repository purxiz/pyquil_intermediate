#!/bin/bash

echo "test"
/usr/bin/screen -dmS qvm /usr/local/bin/qvm -S
/usr/bin/screen -dmS quilc /usr/local/bin/quilc -S
echo "test2"

