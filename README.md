# COMPEIT Server prototype
COMPEIT server framework v2.0 with a sample frontend

## Installation example
The Flask environment is preferably installed in a python virtualenv, [Flask installation](http://flask.pocoo.org/docs/0.10/installation/)

```
prozac:dashboard nogge$ virtualenv venv
New python executable in venv/bin/python
Installing setuptools, pip...done.
prozac:dashboard nogge$ . venv/bin/activate
(venv)prozac:dashboard nogge$ pip install -r requirements.txt
Downloading/unpacking Flask==0.10.1 (from -r requirements.txt (line 1))
  Downloading Flask-0.10.1.tar.gz (544kB): 544kB downloaded
...
    yield from self.wsgi.close()
             ^
SyntaxError: invalid syntax

  Running setup.py install for itsdangerous

    warning: no previously-included files matching '*' found under directory 'docs/_build'
  Running setup.py install for pytz

Successfully installed Flask Flask-Bootstrap ... pytz six
Cleaning up...
```

## Creating a sample database
The database needs to be populated with users and passwords. The sample database is populated in `app/models.py` `create_sample_db()`
```
(venv)prozac:dashboard nogge$ ./manage.py sample_db
````

## Running
The applications binds to all addresses and port 5000 by default. It can be changed in `manage.py` `server()` (`host` and `port` arguments to `run`). The configuration is expected to be moved into `config.py`.
```
(venv)prozac:dashboard nogge$ ./manage.py server
 * Running on http://0.0.0.0:5000/
 * Restarting with reloader
 ```
