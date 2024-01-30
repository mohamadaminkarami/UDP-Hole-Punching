
VENV = .venv
PYTHON = $(VENV)/bin/python3

build:
ifeq (,$(wildcard $(VENV)))
	python3 -m venv $(VENV)
endif

run-server: build
	. $(VENV)/bin/activate
	$(PYTHON) src/stun_server.py

run-client: build
	. $(VENV)/bin/activate
	$(PYTHON) src/client.py

clean:
	rm -rf $(VENV)
