# hookii
hookii scripts and various hacks


### Installation


##### System-wide (root)

	# python setup.py install

Destinations:

- ```/usr/lib/python2.7/site-packages``` for the package 
- ```/usr/bin``` for executables.


##### As current user

	python setup.py install --user

Destinations:

- ```~/.local/lib/python2.7/site-packages``` for the package 
- ```~/.local/bin/``` for executables.


##### In a virtual environment, for testing
Using [virtualenv](https://virtualenv.pypa.io), from the project base directory

	virtualenv2 env
	source env/bin/activate
	python setup.py install


Destinations:

- ```./env/lib/python2.7/site-packages``` for the package 
- ```./env/bin/``` for executables.




### Execution

If the exectutables directory is in **$PATH**, just:

	hookiifier --user admin --pass xxx
