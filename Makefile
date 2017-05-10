
test-all: test-python test-jython test-integration test-launcher

test-python:
	py.test
	
test-jython:
	export CLASSPATH=$(HOME)/lib/Jama-1.0.3.jar:$(CLASSPATH); echo $$CLASSPATH; $(HOME)/jython/bin/py.test
	
test-integration:
	py.test --boxed integration_checks.py
	
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
	
doc-clean:
	cd doc; make clean

help:
	@echo
	@echo "Please use \`make <target>' where <target> is one of"
	@echo
	@echo "  test-all"
	@echo "  test-python"
	@echo "  test-jython"
	@echo "  test-integration"
	@echo "  test-launcher"
	@echo "  install-jython"
	@echo
	@echo "  doc-source  :  to expand *_template.rst to *.rst"
	@echo "  doc-html"
	@echo "  doc-pdf"
	@echo "  doc-all"
	@echo "  doc-clean"
	@echo
