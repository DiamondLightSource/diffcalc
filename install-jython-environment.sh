#!/usr/bin/env sh

JYTHON_URL='https://repo1.maven.org/maven2/org/python/jython-installer/2.7.1/jython-installer-2.7.1.jar'
JAMA_JAR_URL='https://repo1.maven.org/maven2/gov/nist/math/jama/1.0.3/jama-1.0.3.jar'
COMMONS_MATH_URL='https://repo1.maven.org/maven2/org/apache/commons/commons-math3/3.6.1/commons-math3-3.6.1.jar'

# Install jars
wget $JAMA_JAR_URL
wget $COMMONS_MATH_URL
export CLASSPATH=$PWD/jama-1.0.3.jar:$PWD/commons-math3-3.6.1.jar:$CLASSPATH

# Install Jython
wget $JYTHON_URL -O jython_installer.jar
java -jar jython_installer.jar -s -d $HOME/jython

# Install nose for Jython
# TODO: move to a setup.py
$HOME/jython/bin/pip install nose
$HOME/jython/bin/pip install pytest==3.10.1
$HOME/jython/bin/pip install pytest-xdist==1.26.1
