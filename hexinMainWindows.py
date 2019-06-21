# !/usr/bin/python
# Python:   3.6.5
# Platform: Windows/Linux
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  JLink tool (GUI).
# History:  2019-05-29 Ver:0.1 [Heyn] Initialization
#           2019-06-21 Ver:0.2 [Heyn] Bugfixed: exception exit

import time
import threading

import gui.images
import plugins.hexinLogging
from version import __version__

from hexinThreading import programThreading
from drivers.hexinJLink import hexinJLink
from plugins.hexinIntelHex import hexinIntelHex
from gui.mainWindows import Ui_MainWindow

from PyQt5.QtGui  import QIcon
from PyQt5.QtGui  import QColor
from PyQt5.QtCore import QTimer

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView
from PyQt5.QtWidgets import QMenu, QTableWidgetItem, QDialog, QLineEdit, QPushButton
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QFileDialog, QComboBox


class hexinJLinkTool( Ui_MainWindow, QMainWindow ):

    def __init__(self, parent = None):
        super( hexinJLinkTool, self).__init__()
        self.setupUi( self )
        self.setWindowTitle( 'JLinkTool {}'.format( __version__ ) )
        self.setWindowIcon( QIcon(':/icons/hexin.png') )
        self.lineEditStartAddress.setText('0')
        # Init
        self.__init_poll_jlink_timer( 2000 )
        self.__intelHexFilePath, self.__intelHexFile = None, None

    def closeEvent( self, event ):
        reply = QMessageBox.question( self, '提示', '确定要关闭软件吗？', QMessageBox.Yes | QMessageBox.No, QMessageBox.No )
        if reply == QMessageBox.Yes:
            self.poolJLinkTimer.stop()
            event.accept()
        else:
            event.ignore()

    @pyqtSlot()
    def on_actionQuit_triggered( self ):
        self.close()

    def __init_poll_jlink_timer( self, ms=1000 ):
        try:
            jlinkDevice = hexinJLink( )
            jlink = jlinkDevice.scan()
        except BaseException as err:
            self.statusBar().showMessage( '[错误] 加载JLink驱动失败...{}'.format( err ) )
            return

        if ( len( jlink ) == 0 ):
            self.pushButtonStart.setDisabled( True )
        else:
            self.comboBoxJLinkSN.addItems( jlink )

        self.poolJLinkTimer = QTimer( self )
        self.poolJLinkTimer.start( ms )
        self.poolJLinkTimer.timeout.connect( self.pollJLinkSlot )

    def pollJLinkSlot( self ):
        jlinkDevice = hexinJLink( ) # Bugfixed: 2019-06-21 exception exit
        jlink = jlinkDevice.scan()
        items = [ self.comboBoxJLinkSN.itemText( i ) for i in range( self.comboBoxJLinkSN.count() ) ]
        
        if ( len( jlink ) == 0 ):
            self.pushButtonStart.setDisabled( True )
            self.comboBoxJLinkSN.clear()
            self.statusBar().showMessage( '[错误] 未检测到JLink设备...' )

        if ( jlink != items ):
            self.comboBoxJLinkSN.clear()
            self.comboBoxJLinkSN.addItems( jlink )
            self.pushButtonStart.setDisabled( False )
            self.statusBar().showMessage( '' )

    @pyqtSlot()
    def on_actionImport_triggered( self ):
        filename, filetype = QFileDialog.getOpenFileName( self,
                                                          '导入HEX文件',
                                                          './hex/',
                                                          filter='Hexin(*.hex)' )
        if filename == ' ':
            return

        self.__intelHexFilePath = filename
        try:
            self.__intelHexFile = hexinIntelHex( self.__intelHexFilePath )
            self.lineEditStartAddress.setText( '0x{:08X}'.format( self.__intelHexFile.minaddress() ) )
        except BaseException as err:
            self.statusBar().showMessage( '加载HEX数据失败:{}.'.format( err ) )
            return
        self.statusBar().showMessage( '加载HEX数据成功:{}.'.format( self.__intelHexFilePath ) )

    @pyqtSlot()
    def on_pushButtonStart_clicked( self ):
        device  = self.lineEditDevice.text()

        if self.__intelHexFile is None:
            QMessageBox.warning( self, '警告', '请先导入Hex文件后，再进行烧录！', QMessageBox.Yes )
            return

        mainthread = threading.Thread( name   = 'programThreading',
                                       target = programThreading,
                                       daemon = True,
                                       args   = ( self.__programThreadingLogs_cb,
                                                  self.comboBoxJLinkSN.currentText(),
                                                  device,
                                                  self.__intelHexFilePath,
                                                  self.__intelHexFile.minaddress( ) )
                                        )
        mainthread.start()

    def __programThreadingLogs_cb( self, logs ):
        self.statusBar().showMessage( '{}'.format(logs) )
