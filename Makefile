
test-all: test-python test-jython test-integration test-launcher

test-python:
	nosetests
	
test-jython:
	export CLASSPATH=$(HOME)/lib/Jama-1.0.3.jar:$(CLASSPATH); echo $$CLASSPATH; $(HOME)/jython/bin/nosetests
	
test-integration:
	nosetests --with-process-isolation integration_checks.py
	
test-launcher:
	./diffcalc.py --help
	./diffcalc.py --modules
	./diffcalc.py --non-interactive --python sixcircle

install-jython:
	./install-jython-environment.sh
	
doc-source:
	./diffcalc.py --non-interactive --make-manuals-source

doc-html:
	cd doc; make html
	
doc-pdf:
	cd doc; make pdf
	
doc-all:
	cd doc; make all
	
make doc-clean:
	cd doc; make clean

help:
	@echo
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "        to make standalone HTML files"
	@echo "  pdf       to create pdf files for both A4- and Letter-sized paper"
	@echo "  pdfa4     to create pdf files for A4-sized paper"
	@echo "  pdfletter to create pdf files for Letter-sized paper"
	@echo "  all       to build html and pdf"
	@echo "  clean     to wipe the build directory"
	@echo
