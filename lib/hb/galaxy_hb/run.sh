#!/bin/sh

# User settings
ulimit -s unlimited

# Python
export PYTHONPATH=$HB_SOURCE_CODE_BASE_DIR:$GALAXY_LIB_PATH:$HB_PYTHONPATH

# R
export RHOME=$HB_RHOME
export R_LIBS=$HB_R_LIBS_DIR:$HB_R_LIBS

# Xvfb
export DISPLAY=$HB_XVFB_DISPLAY

# Tmp dir
export TMPDIR=$GALAXY_NEW_FILE_PATH
export TMP=$TMPDIR
export TEMP=$TMPDIR
export PYTHON_EGG_CACHE="$TMP/.python-eggs"

# Galaxy
cd `dirname $0`

python ./scripts/check_python.py
[ $? -ne 0 ] && exit 1

SAMPLES="
    external_service_types_conf.xml.sample
    datatypes_conf.xml.sample
    reports_wsgi.ini.sample
    tool_conf.xml.sample
    tool_data_table_conf.xml.sample
    universe_wsgi.ini.sample
    tool-data/shared/ucsc/builds.txt.sample
    tool-data/*.sample
    static/welcome.html.sample
"

# Create any missing config/location files
for sample in $SAMPLES; do
    file=`echo $sample | sed -e 's/\.sample$//'`
    if [ ! -f "$file" -a -f "$sample" ]; then
        echo "Initializing $file from `basename $sample`"
        cp $sample $file
    fi
done

# explicitly attempt to fetch eggs before running. Also start and stop Xfvb as appropriate
FETCH_EGGS=1
START_XVFB=0
STOP_XVTB=0
for arg in "$@"; do
    [[ "$arg" = "--stop-daemon" || "$arg" = "stop" ]] && FETCH_EGGS=0 && STOP_XVFB=1
    [[ "$arg" = "--daemon" || "$arg" = "start" ]] && START_XVFB=1
done
if [ $FETCH_EGGS -eq 1 ]; then
    python ./scripts/check_eggs.py quiet
    if [ $? -ne 0 ]; then
        echo "Some eggs are out of date, attempting to fetch..."
#        python ./scripts/fetch_eggs.py
        python ./scripts/scramble.py
        python ./scripts/hb_scramble.py
        if [ $? -eq 0 ]; then
            echo "Fetch successful."
        else
            echo "Fetch failed."
            exit 1
        fi
    fi
fi
if [ $START_XVFB -eq 1 ]; then
    echo 'Starting Xvfb on display $HB_XVFB_DISPLAY'
    Xvfb $HB_XVFB_DISPLAY -screen 0 1600x1200x24 -nolisten tcp >$LOG_PATH/xvfb.log 2>&1 &
elif [ $STOP_XVFB -eq 1 ]; then
    echo 'Stopping Xvfb on display $HB_XVFB_DISPLAY'
    pkill -f "Xvfb $HB_XVFB_DISPLAY"
fi

python ./scripts/paster.py serve universe_wsgi.ini $@
