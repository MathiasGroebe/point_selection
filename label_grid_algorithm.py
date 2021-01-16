# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LabelGrid
                                 A QGIS plugin
 Select points in grid cells
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
"""

__author__ = 'Mathias Gröbe'
__date__ = '2020-12-07'
__copyright__ = '(C) 2020 by Mathias Gröbe'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import (QCoreApplication, QVariant)
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterEnum,
                       QgsWkbTypes,
                       QgsGeometry,
                       QgsFields,
                       QgsField,
                       QgsFeature,
                       QgsProcessingUtils)
import os, processing

class LabelGridAlgorithm(QgsProcessingAlgorithm):


    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    MINMAX = 'MINMAX'
    VALUE_FIELD = 'VALUE_FIELD'
    FIELD_FOR_GRID_ID = 'FIELD_FOR_GRID_ID'
    FIELD_FOR_SELECTION = 'FIELD_FOR_SELECTION'
    GRID_TYPE = 'GRID_TYPE'
    GRID_SIZE = 'GRID_SIZE'

    def initAlgorithm(self, config):

        # Here we define the inputs and output of the algorithm


        # Input point layer
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        
        # Field in point layer with numeric values
        self.addParameter(
            QgsProcessingParameterField(
            self.VALUE_FIELD,
            self.tr('Field with numeric values'),
            None,
            self.INPUT,
            QgsProcessingParameterField.Numeric)
        )

        # Select min or max
        self.addParameter(
            QgsProcessingParameterEnum(
            self.MINMAX,
            self.tr('Use max or min values'),
            options = ['Max', 'Min'],
            defaultValue = 0,
            optional = False)
        )  
        
        # Set grid size
        self.addParameter(
            QgsProcessingParameterNumber(
            self.GRID_SIZE,
            self.tr('Size of grid cells'),
            QgsProcessingParameterNumber.Integer,
            10000,
            False,
            1,)
        )     

        # Select grid shape
        self.addParameter(
            QgsProcessingParameterEnum(
            self.GRID_TYPE,
            self.tr('Choose shape of the used grid cells'),
            options = ['Rectangle', 'Diamond', 'Hexagon'],
            defaultValue = 0,
            optional = False)
        )
        
        # Chose field to grid id
        self.addParameter(
            QgsProcessingParameterField(
            self.FIELD_FOR_GRID_ID,
            self.tr('Field for storing the id of the used grid cell'),
            None,
            self.INPUT,
            QgsProcessingParameterField.Numeric)
        )

        # Chose field to selection
        self.addParameter(
            QgsProcessingParameterField(
            self.FIELD_FOR_SELECTION,
            self.tr('Field for marking the selected points'),
            None,
            self.INPUT,
            QgsProcessingParameterField.Numeric)
        )        
        
        # Output points
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_POINTS,
                self.tr('Label Grid Points')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # Here is where the processing itself takes place.

        # Retrieve the feature source and sink.
        
        source = self.parameterAsSource(parameters, self.INPUT, context)
        
        # Add new fields and combine with existing ones
        # See https://github.com/qgis/QGIS/blob/master/python/plugins/processing/algs/qgis/Climb.py
        # in_fields = source.fields()
        # new_fields = QgsFields()
        # new_fields.append(QgsField("grid_id", QVariant.Int))
        # out_fields = QgsProcessingUtils.combineFields(in_fields, new_fields)
        
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, source.fields(), source.wkbType(), source.sourceCrs())
                
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        if QgsWkbTypes.isMultiType(source.wkbType()):
            raise QgsProcessingException(self.tr('Input layer is a MultiPoint layer - first convert to single points before using this algorithm.'))
                
        # Get variables
        value_field = self.parameterAsString(parameters, self.VALUE_FIELD, context)
        minmax_input = self.parameterAsString(parameters, self.MINMAX, context)
        field_for_selection = self.parameterAsString(parameters, self.FIELD_FOR_SELECTION, context)
        field_for_grid_id = self.parameterAsString(parameters, self.FIELD_FOR_GRID_ID, context)
        grid_type = self.parameterAsString(parameters, self.GRID_TYPE, context)
        grid_size = self.parameterAsString(parameters, self.GRID_SIZE, context)
        
        # Translate grid type
        creategrid_grid_type = 2
        if grid_type == '0': creategrid_grid_type = 2 # Rectangle
        if grid_type == '1': creategrid_grid_type = 3 # Diamond
        if grid_type == '2': creategrid_grid_type = 4 # Hexagon
        
        # Create grid
        grid = processing.run("qgis:creategrid", {'CRS': source.sourceCrs(), 'TYPE': creategrid_grid_type, 'EXTENT': source.sourceExtent().buffered(float(grid_size) * 0.66), 'HSPACING': grid_size, 'VSPACING': grid_size, 'HOVERLAY': 0, 'VOVERLAY': 0, 'OUTPUT': 'memory:'})

        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0

        # check which point is in which grid cell
        points = source.getFeatures()
        point_dict = {}
        # point id, grid id, value

        for current, point in enumerate(points):
            if feedback.isCanceled():
                break            
            grid_cells = grid['OUTPUT'].getFeatures()
            check = True
            for cell in grid_cells:
                if cell.geometry().contains(point.geometry()):
                    point_dict[point.id()] = [cell.id(), point[value_field]]
                    check = False

            # if point is not cotained by one grid cell set values
            if check:
                point_dict[point.id()] = [-1, None]

            # Update progress
            feedback.setProgress(int(current * total))

        
        # search for highest/lowest value
        grid_dict = {}
        # grid id, highes/lowest value, id of point
        
        # Handle input for min/max
        minmax = 'max'
        if minmax_input == '1': minmax = 'min'  
        

        for point_key, point_value in point_dict.items():
            if feedback.isCanceled():
                break
                
            # stop if no value or no grid cell
            if point_value[1] is not None:
             
                
                # check if grid is already known
                if point_value[0] in grid_dict:

                    if minmax == 'min':
                        # if known, check if dict contains lowest value
                        if point_value[1] < grid_dict.get(point_value[0])[0]:
                            # update value
                            grid_dict[point_value[0]] = [point_value[1], point_key]

                    if minmax == 'max':
                        # if known, check if dict contains highest value
                        if point_value[1] > grid_dict.get(point_value[0])[0]:
                            # update value
                            grid_dict[point_value[0]] = [point_value[1], point_key]
                # add point
                else:
                    # add point with grid_id and value to dict
                    grid_dict[point_value[0]] = [point_value[1], point_key]
                
        # bring values to features
        features = source.getFeatures()

        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            # set grid_id 
            if feature.id() in point_dict:
                grid_id = point_dict.get(feature.id())[0]
                # write grid_id to point
                feature[field_for_grid_id] = point_dict.get(feature.id())[0]
                # check if point is selected
                try:
                    if grid_dict.get(grid_id)[1] == feature.id():
                        feature[field_for_selection] = 1
                    else:
                        feature[field_for_selection] = 0
                except:
                    feature[field_for_selection] = 0

            # Add a feature in the sink
            sink.addFeature(feature, QgsFeatureSink.FastInsert)

            # Update the progress bar
            feedback.setProgress(int(current * total))

        # Return the results of the algorithm.
        return {self.OUTPUT: dest_id}

    def name(self):
        """
        Returns the algorithm name
        """
        return 'Label Grid'

    def displayName(self):
        """
        Returns the translated algorithm name
        """
        return 'Label Grid' 

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''
        
    def icon(self):
        return QIcon(self.svgIconPath())


    def svgIconPath(self):
        return os.path.dirname(__file__) + '/label_grid_icon.png'
        
    def shortHelpString(self):
        file = os.path.dirname(__file__) + '/label_grid.help'
        if not os.path.exists(file):
            return ''
        with open(file) as helpfile:
            help = helpfile.read()
        return help        

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LabelGridAlgorithm()
