__author__ = 'Mathias Gröbe'
__date__ = '2025-11-25'
__copyright__ = '(C) 2025 by Mathias Gröbe'

import os
import configparser

class PointSelectionTools:

    @staticmethod
    def getPluginVersion() -> str:
        """
        Returns the plugin version.
        """

        metadata = configparser.ConfigParser()
        metadata.read(os.path.join(os.path.dirname(__file__), "metadata.txt"))

        return metadata['general']['version']
    
    @staticmethod
    def getPluginName() -> str:
        """
        Returns the plugin name.
        """

        metadata = configparser.ConfigParser()
        metadata.read(os.path.join(os.path.dirname(__file__), "metadata.txt"))

        return metadata['general']['name']