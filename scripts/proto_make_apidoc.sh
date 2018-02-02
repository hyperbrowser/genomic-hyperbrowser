#!/bin/bash 

GALAXY_DIR=$(realpath $(dirname $0)/..)
echo $GALAXY_DIR
LIB_DIR=$GALAXY_DIR/lib
PROTO_DOC_DIR=$LIB_DIR/proto/doc
STATIC_PROTO_DOC_DIR=$GALAXY_DIR/static/proto/doc

rm $PROTO_DOC_DIR/proto*.rst $PROTO_DOC_DIR/modules.rst

cd $LIB_DIR
EXCLUDE_PATHS=$(find proto \( -path proto/doc -o -path proto/__init__.py -o -path proto/config/__init__.py -o -path proto/tools/__init__.py -o -path proto/CommonFunctions.py -o -path proto/HtmlCore.py -o -path proto/TextCore.py -o -path proto/TableCoreMixin.py -o -path proto/RSetup.py -o -path proto/StaticFile.py -o -path proto/config/Config.py -o -path proto/tools/ToolTemplate.py \) -prune -o -name "*.py" -print)
sphinx-apidoc -e -o $PROTO_DOC_DIR proto/ proto/doc $EXCLUDE_PATHS

cd $PROTO_DOC_DIR
make clean html

rm -rf $STATIC_PROTO_DOC_DIR/html
mv _build/html $STATIC_PROTO_DOC_DIR/html

make clean
