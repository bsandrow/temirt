
try:
    from setuptools import setup
except ImportError:
    print "Falling back to distutils. Functionality may be limited."
    from distutils.core import setup

config = {
    'description'       : 'A Python interface to the Trimet Web API',
    'author'            : 'Brandon Sandrowicz',
    'url'               : 'http://github.com/bsandrow/pmet',
    'author_email'      : 'brandon@sandrowicz.org',
    'version'           : 0.1,
    'install_requires'  : ['requests', 'lxml'],
    'packages'          : ['pmet'],
    'name'              : 'Pmet',
}

setup(**config)
