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
#$HOME/jython/bin/pip install nose==1.3.7
#$HOME/jython/bin/pip install pytest==3.10.1
#$HOME/jython/bin/pip install pytest-xdist==1.26.1


# Download dependencies directly from Pypi
# as pip is currently broken (https://github.com/jython/jython/issues/97)


wget https://files.pythonhosted.org/packages/02/ee/b6e02dc6529e82b75bb06823ff7d005b141037cb1416b10c6f00fc419dca/Pygments-2.2.0-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/a1/4e/c42167ba5c3192bed633726d39d7896cc55d4fa3ec4a1fb60cd3a53fc4c7/decorator-4.1.2-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/70/c7/e8cb4a537ee4fc497ac80a606a667fd1832f28ad3ddbfa25bf30473eae13/pytest-4.6.11-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/d9/5a/e7c31adbe875f2abbb91bd84cf2dc52d792b5a01506781dbcf25c91daf11/six-1.16.0-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/2c/a0/da5f49008ec6e9a658dbf5d7310a4debd397bce0b4db03cf8a410066bb87/atomicwrites-1.4.0-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/f6/f0/10642828a8dfb741e5f3fbaac830550a518a775c7fff6f04a007259b0548/py-1.11.0-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/be/be/7abce643bfdf8ca01c48afa2ddf8308c2308b0c3b239a44e57d020afa0ef/attrs-21.4.0-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/a0/28/85c7aa31b80d150b772fbe4a229487bc6644da9ccb7e427dd8cc60cb8a62/pluggy-0.13.1-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/c1/f9/9058661f6b4bb017dfe17ef84b461e4b11130c7bbee1b35cc0883ec8533b/importlib_metadata-2.1.2-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/96/0a/67556e9b7782df7118c1f49bdc494da5e5e429c93aa77965f33e81287c8c/zipp-1.2.0-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/cf/e5/989798d38831a8505d62687c94b0f2954ff0a40782e25f9add8ed675dc1f/contextlib2-0.6.0-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/7a/2a/95ed0501cf5d8709490b1d3a3f9b5cf340da6c433f896bbe9ce08dbe6785/configparser-4.0.2-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/76/67/dc02c72177ec79f0176e5bf9921e9c1745a381ed556afb3b3ecc2bb8ba2e/pathlib2-2.3.6-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/f9/d0/6b7b38eaf9964510f5c32aa5aaf9f419864d2e0ebe34274e6cba5689a0c5/scandir-1.10.0-cp27-cp27m-win_amd64.whl
wget https://files.pythonhosted.org/packages/3e/89/7ea760b4daa42653ece2380531c90f64788d979110a2ab51049d92f408af/packaging-20.9-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/69/cb/f5be453359271714c01b9bd06126eaf2e368f1fddfff30818754b5ac2328/funcsigs-1.0.2-py2.py3-none-any.whl
wget https://files.pythonhosted.org/packages/a4/a6/42f17d065bda1fac255db13afc94c93dbfb64393eae37c749b4cb0752fc7/more_itertools-5.0.0-py3-none-any.whl
wget https://files.pythonhosted.org/packages/99/4f/13fb671119e65c4dce97c60e67d3fd9e6f7f809f2b307e2611f4701205cb/nose-1.3.7-py2-none-any.whl

unzip -d $HOME/jython/Lib/site-packages Pygments-2.2.0-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages decorator-4.1.2-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages pytest-4.6.11-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages six-1.16.0-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages atomicwrites-1.4.0-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages py-1.11.0-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages attrs-21.4.0-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages pluggy-0.13.1-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages importlib_metadata-2.1.2-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages zipp-1.2.0-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages contextlib2-0.6.0-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages configparser-4.0.2-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages pathlib2-2.3.6-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages scandir-1.10.0-cp27-cp27m-win_amd64.whl
unzip -d $HOME/jython/Lib/site-packages packaging-20.9-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages funcsigs-1.0.2-py2.py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages more_itertools-5.0.0-py3-none-any.whl
unzip -d $HOME/jython/Lib/site-packages nose-1.3.7-py2-none-any.whl
