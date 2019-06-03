# !/usr/bin/python
# Python:   3.6.5
# Platform: Windows/Linux
# Author:   Heyn (heyunhuan@gmail.com)
# Program:  hexin J-Link.
# History:  2019-05-27 Ver:0.1 [Heyn] Initialization

import os
import re
import time
import pylink
import logging

class hexinJLink( object ):

    def catchException( origin_func ):
        def wrapper( self, *args, **kwargs ):
            try:
                return origin_func( self, *args, **kwargs )
            except BaseException as err:
                logging.error( str( err) )
                return False
        return wrapper
    
    # logger = logging.getLogger()
    # logger.setLevel( logging.DEBUG )

    def __init__( self, jlink_dll_path='JLinkARM.dll' ):
        self.__jlink = None
        self.jlink_dll_path = jlink_dll_path if os.path.exists( jlink_dll_path ) else None

    @catchException
    def scan( self ):
        jlink = []
        info = pylink.JLink( lib=pylink.library.Library( dllpath=self.jlink_dll_path ) ).connected_emulators( host=pylink.enums.JLinkHost.USB )
        for item in info:
            logging.info( item )
            jlink.extend( re.findall( r'\d+\.?\d*', str( item ) ) )
        return jlink

    @catchException
    def connect( self, sn, chip='Cortex-M4', interface='SWD' ):
        self.__jlink = pylink.JLink( lib=pylink.library.Library( dllpath=self.jlink_dll_path ) )
        self.__jlink.exec_command( 'DisableAutoUpdateFW' )
        self.__jlink.disable_dialog_boxes()
        self.__jlink.open( sn )

        logging.debug( 'JLink S/N {}'.format( sn ) )

        if interface == 'JTAG':
            self.__jlink.set_tif( pylink.enums.JLinkInterfaces.JTAG )
        else:
            self.__jlink.set_tif( pylink.enums.JLinkInterfaces.SWD )

        self.__jlink.connect( chip, speed=4000, verbose=True )
        self.__jlink.set_reset_strategy( pylink.enums.JLinkResetStrategyCortexM3.RESETPIN )
        return True

    def vtarget( self ):
        status  = self.__jlink.hardware_status
        voltage = re.findall( r'\d+\=?\d*', str( status ) )
        logging.debug( '{}'.format( status ) )
        return int( voltage[0] ) / 1000

    def cpu_core_id( self ):
        """ Get CPU core identifiers.
        """
        self.__core_id  = self.__jlink.core_id( )
        self.__core_cpu = self.__jlink.core_cpu()

        logging.info( 'Core ID  : 0x{:08X}'.format( self.__core_id ) )
        logging.info( 'Core CPU : 0x{:08X}'.format( self.__core_cpu ) )
        logging.info( 'Core Name: {}'.format( self.__jlink.core_name() ) )
        logging.info( 'Device Family: 0x{:02X}'.format( self.__jlink.device_family() ) )

        return self.__core_id

    def halt( self ):
        """ Halts the CPU Core.
            Returns:
                ``True`` if halted, ``False`` otherwise.
        """
        ret = self.__jlink.halt()
        logging.debug( 'JLink halt  : {}'.format( ret ) )
        return ret

    def reset( self ):
        logging.debug( 'JLink reset : {}'.format( self.__jlink.reset( ) ) )
        return True

    @catchException
    def download_file( self, hexfile=None, address=0x8000000, autostart=False, on_progress=None ):
        if not os.path.exists( hexfile ):
            logging.error( 'Hex file<{}> does not exist!'.format( hexfile ) )
            return False
        #self.erase_chip( )
        time.sleep( 0.2 )
        progress = on_progress if on_progress else self.__progress
        self.__jlink.flash_file( hexfile, address, on_progress=progress )

        if autostart:
            self.__jlink.exec_app( address )
        return True

    def __progress( self, action, progress_string, percentage ):
        """ Down load file callback.

            action          : [ b'Program', b'Erase', b'Verify', b'Compare' ]

            progress_string : [ b'Comparing range 0x08000000 - 0x08003FFF (16 KB)',
                                b'Programming range 0x08000000 - 0x08000FFF (4 KB)',
                                b'Verifying range 0x08000000 - 0x08003FFF (16 KB)' ]

            percentage      : 0% - 100%
        """
        logging.info( 'Action {}'.format( action ) )
        logging.info( 'Progress string {}'.format( progress_string ) )
        logging.info( 'Percentage {}'.format( percentage ) )

    def run( self, address ):
        self.__jlink.exec_app( address )

    @catchException
    def unique_device_id( self, address=0x1FFF7A10, size=3 ):
        """ Get stm32xxx cpu id ( 96bits )
            address :   stm32f103 -> 0x1FFFF7E8
                        stm32f405 / stm32f407  -> 0x1FFF7A10
        """
        buffer = self.__jlink.memory_read32( address, size )
        return ''.join( [ '{:08X}'.format(x) for x in buffer ] )

    @catchException
    def erase_chip( self ):
        self.__jlink.erase( )

    @catchException
    def disconnect( self ):
        if not self.__jlink:
            return
        #self.__jlink.reset( )
        self.__jlink.restart( )
        self.__jlink.close( )
        self.__jlink = None


# jlink = hexinJLink()
# jdev  =  jlink.scan()
# print(jlink.connect( sn=jdev[0], chip='STM32F405RG' ))
# # jlink.reset()
# jlink.cpu_core_id( )
# print(jlink.unique_device_id())
# print(jlink.vtarget())

