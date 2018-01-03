#!/usr/bin/env sh

JYTHON_URL='http://search.maven.org/remotecontent?filepath=org/python/jython-installer/2.7.1/jython-installer-2.7.1.jar'
JAMA_JAR_URL='http://math.nist.gov/javanumerics/jama/Jama-1.0.3.jar'

# Install Jama jar
mkdir -p lib
wget -P $HOME/lib $JAMA_JAR_URL
export CLASSPATH=$HOME/lib/Jama-1.0.3.jar:$CLASSPATH

# Install Jython
wget $JYTHON_URL -O jython_installer.jar
java -jar jython_installer.jar -s -d $HOME/jython

# Install nose for Jython
# TODO: move to a setup.py
$HOME/jython/bin/pip install nose
$HOME/jython/bin/pip install pytest
$HOME/jython/bin/pip install pytest-xdist
