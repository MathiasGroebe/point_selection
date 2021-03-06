# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PointSelection
                                 A QGIS plugin
 Calculates the discrete isolation
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-12-07
        copyright            : (C) 2020 by Mathias Gröbe
        email                : mathias.groebe@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Mathias Gröbe'
__date__ = '2020-12-07'
__copyright__ = '(C) 2020 by Mathias Gröbe'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PointSelection class from file PointSelection.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .point_selection import PointSelectionPlugin
    return PointSelectionPlugin()
