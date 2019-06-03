# !/usr/bin/python
# Python:   3.6.5
# Platform: Windows/Linux
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  JLink tool.
# History:  2019-05-29 Ver:0.1 [Heyn] Initialization


import sys
from PyQt5.QtWidgets  import QApplication
from hexinMainWindows import hexinJLinkTool

if __name__ == '__main__':
    app = QApplication( sys.argv )
    main = hexinJLinkTool( )
    main.show( )
    sys.exit( app.exec_( ) )
