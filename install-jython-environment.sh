#!/usr/bin/env sh

JYTHON_URL='http://search.maven.org/remotecontent?filepath=org/python/jython-installer/2.5.3/jython-installer-2.5.3.jar'
JAMA_JAR_URL='http://math.nist.gov/javanumerics/jama/Jama-1.0.3.jar'

# Install Jama jar
mkdir -p lib
wget -P $HOME/lib $JAMA_JAR_URL
export CLASSPATH=$HOME/lib/Jama-1.0.3.jar:$CLASSPATH

# Install Jython
wget $JYTHON_URL -O jython_installer.jar
java -jar jython_installer.jar -s -d $HOME/jython

# Install Setuptools
SETUPTOOLS_FILE='1.4.2.tar.gz'
SETUPTOOLS_URL='https://github.com/pypa/setuptools/archive/1.4.2.tar.gz'
wget -P $HOME/lib $SETUPTOOLS_URL
tar xvzf $HOME/lib/1.4.2.tar.gz -C $HOME/lib
cd $HOME/lib/setuptools-1.4.2
$HOME/jython/bin/jython setup.py install --prefix=$HOME/jython
cd $HOME

# Install nose and pytest for Jython
# TODO: move to a setup.py
$HOME/jython/bin/easy_install "py==1.4.19"
$HOME/jython/bin/easy_install "nose==1.3.4"
$HOME/jython/bin/easy_install "pytest==2.5.0"
$HOME/jython/bin/easy_install "execnet==1.1"
$HOME/jython/bin/easy_install "pytest-xdist==1.9.0"
