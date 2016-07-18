#!/bin/bash

./venv/bin/python -c "import sys; import frinkiaccommands; print frinkiaccommands.do_stuff(sys.argv[1]);" "$*"
