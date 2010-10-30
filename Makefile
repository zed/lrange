.PHONY: default help

default: help

help:
	@echo "Available commands:"
	@sed -n '/^[-a-zA-Z0-9_][-a-zA-Z0-9_.]*:/s/:.*//p' <Makefile | sort

distclean:
	-find \( -name '*.py[co]' -o -name '*$py.class' -type f \) -print0 | xargs -0 rm
	-rm cover htmlcov __pycache__ lrange.egg-info .tox .coverage *,cover -r

