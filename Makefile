.PHONY: test coverage clean distclean

RM = rm -rf
PYTHON = python3

test: clean
	export PYTEST_ADDOPTS="-p no:cacheprovider --verbose --capture=no ."
	$(PYTHON) setup.py test

coverage: clean
	export PYTEST_ADDOPTS="-p no:cacheprovider --verbose --cov=oauth2 --cov-report=term --cov-config .coveragerc --capture=no ."
	$(PYTHON) setup.py test

clean:
	@$(RM) build/ *.egg-info/ .eggs/ dist/
	@find . \( \
		-iname "*.pyc" \
		-or -iname "*.pyo" \
		-or -iname "*.so" \
		-or -iname "*.o" \
		-or -iname "*~" \
		-or -iname "._*" \
		-or -iname "*.swp" \
		-or -iname "Desktop.ini" \
		-or -iname "Thumbs.db" \
		-or -iname "__MACOSX__" \
		-or -iname ".DS_Store" \
		\) -delete

distclean: clean
	@$(RM) \
		dist/ \
		bin/ \
		develop-eggs/ \
		eggs/ \
		parts/ \
		MANIFEST \
		htmlcov/ \
		.coverage \
		.installed.cfg