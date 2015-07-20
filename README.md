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

If the exectutables directory is in **$PATH**, just execute it with:

	hookiifier --user admin --pass xxx

##### Help message

    usage: hookiifier [-h] [--database DATABASE] [--user USER] --password PASSWORD
                    [--directory DIRECTORY] [--last-run-file LAST_RUN_FILE]
                    [--deltat DELTAT] [--force] [--today]
                    [--loglevel {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}]
                    [--version]

    Hookii archiver.

    optional arguments:
    -h, --help            show this help message and exit
    --database DATABASE   database name
    --user USER           database user
    --password PASSWORD, --pass PASSWORD
                            database password
    --directory DIRECTORY
                            output directory
    --last-run-file LAST_RUN_FILE
                            file with timestamp of last run
    --deltat DELTAT       chunk size for db querying, in days
    --force               also render closed posts
    --today               render only posts from last day
    --loglevel {CRITICAL,ERROR,WARNING,INFO,DEBUG,NOTSET}
    --version             show program's version number and exit

##### Functioning

`hookifiier` now works incrementally, rendering only posts with new comments from the
last execution. The timestamp is saved by default in `/tmp/hookiifier-last-run`, but the file can be specified with `--last-run-file` parameter.

If the file can't be read, all posts are rendered. In this mode the database is queried
in chunks to avoid keeping all the content in memory. The default chunk size is 30 days, meaning that one query retrives posts created in a time span of 30 days, and can be changed with `--deltat` (in days).
