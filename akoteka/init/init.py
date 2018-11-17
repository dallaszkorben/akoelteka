import os
import configparser

def getInit():
    
    file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'init.ini')
    parser = configparser.RawConfigParser()
    parser.read( file )

    version = "0.0.0"
    name = "akoteka"
    title = 'akoTeka'

    try:
        version = parser.get("DEFAULT", 'version')
        name = parser.get("DEFAULT", 'name')
        title = parser.get("DEFAULT", 'title')
    except (configparser.NoSectionError, configparser.NoOptionError):
        pass

    return dict([ 
        ('name', name), 
        ('title', title), 
        ('version', version)
    ])
