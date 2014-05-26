Home Automator
==============

A library to transmit 433mhz signal from a RaspberryPi, wrapped in a REST API.

Contains the ability to transmit raw 32bit codes, and also the ability to switch these:

http://www.maplin.co.uk/remote-controlled-mains-sockets-5-pack-348217


Requires one of these:

http://proto-pic.co.uk/434mhz-rf-link-transmitter/

Installation
------------

Requires WiringPi-Python:

    git clone https://github.com/WiringPi/WiringPi-Python.git
    cd WiringPi-Python/
    git submodule update --init
    sudo apt-get install python2.7-dev python-setuptools
    sudo python setup.py install

Then to install home-automator:

    git clone https://github.com/dmariash/home-automator.git
    cd home-automator/
    pip install -r requirements.txt
    export USERNAME=<your_username>
    export PASSWORD=<your_password>


Running
-------

Needs to be run as root -

    sudo python main.py