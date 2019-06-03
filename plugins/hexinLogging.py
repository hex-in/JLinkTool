# !/usr/bin/python
# Python:   3.6.5
# Platform: Windows/Linux
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  hexin log module.
# History:  2019-05-20 Ver:0.1 [Heyn] Initialization

import os
import json
import logging.config

def hexinLoggingConfig( default_path='hexinlogging.json', default_level=logging.INFO ):
    if os.path.exists( default_path ):
        with open( default_path, 'r' ) as fd:
            try:
                config = json.load( fd )
                logging.config.dictConfig( config )
            except BaseException as err:
                logging.basicConfig( filename='logging.log',
                                     filemode='a',
                                     level=default_level,
                                     format='%(levelname)-8s - %(asctime)s - %(message)s', )
                logging.error( 'Load logging config failed. {}'.format( err ) )
    else:
        logging.basicConfig( level  = default_level,
                             format = '%(levelname)-8s - %(asctime)s - %(message)s', )

hexinLoggingConfig( './ini/hexinlogging.json' )