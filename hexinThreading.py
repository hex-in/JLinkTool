# !/usr/bin/python
# Python:   3.6.5
# Platform: Windows/Linux
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  hexin threading.
# History:  2019-05-30 Ver:0.1 [Heyn] Initialization

import time
import queue
from PyQt5 import QtCore

from drivers.hexinJLink import hexinJLink

class Communicate( QtCore.QObject ):
    logsignal   = QtCore.pyqtSignal( str  )


def programThreading( logscallback, jlinkSN, device, hexfile, address ):
    hexinSlot = Communicate()
    hexinSlot.logsignal.connect ( logscallback )

    def on_progress( action, progress_string, percentage ):
        hexinSlot.logsignal.emit( '{}-{}%'.format( action.decode('utf-8'), percentage ) )

    hexinSlot.logsignal.emit('开始烧录')
    jlink = hexinJLink()


    while True:
        jlink.connect( sn=jlinkSN, chip=device )

    try:
        jlink.connect( sn=jlinkSN, chip=device )
        jlink.reset()
        jlink.halt()
        jlink.download_file( hexfile, address, False, on_progress )
    except BaseException as err:
        hexinSlot.logsignal.emit( '烧录失败:{}'.format( err ) )

    hexinSlot.logsignal.emit('烧录成功')
