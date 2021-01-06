.PHONY: help run test
help :
	@echo "Use this make file to execute the following targets: "
	@echo "* run: run against the test case"
	@echo "* test: run unittests"
	@echo "* clean: clean the created image"

test:
	python -m unittest ex2_test.py 

run:
	python ex2.py ./datasets/hill-ir-rot-0007.png ./datasets/hill-rgb-0007.png
