Testing
=======

1. Install tox (``pip install tox``)
2. Run ``tox``

If you want to test against other versions of Python then you might need to
install them, too. Here's a quick log for installing them in Ubuntu (probably
just as relevant for Debian)::

	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt-get update
	sudo apt-get install pythonX.Y pythonX.Y-dev

	sudo apt-get install build-essential python-dev python3-dev
	sudo apt-get install libjpeg8-dev zlib1g-dev

For Ubuntu >=16.04, you'll also want::

    sudo apt-get install python3.4 python3.4-dev
