# -*- coding: utf-8 -*-

"""
/***************************************************************************
 DiscreteIsolation
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
"""

__author__ = 'Mathias Gröbe'
__date__ = '2020-12-07'
__copyright__ = '(C) 2020 by Mathias Gröbe'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterNumber,
                       QgsWkbTypes,
                       QgsDistanceArea)
import os

class DiscreteIsolationAlgorithm(QgsProcessingAlgorithm):


    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    INPUT = 'INPUT'
    ISOLATION_VALUE_FIELD = 'ISOLATION_VALUE_FIELD'
    MAX_ISOLATION = 'MAX_ISOLATION'
    FIELD_FOR_ISOLATION = 'FIELD_FOR_ISOLATION'

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
            self.ISOLATION_VALUE_FIELD,
            'Field with numeric values',
            None,
            self.INPUT,
            QgsProcessingParameterField.Numeric)
        )
        
        # Max isolation value and search distance
        self.addParameter(
            QgsProcessingParameterNumber(
            self.MAX_ISOLATION,
            'Maximal isolation value',
            QgsProcessingParameterNumber.Integer,
            1000000,
            False,
            1,)
        )     
        
        # Chose field to store isolation values
        self.addParameter(
            QgsProcessingParameterField(
            self.FIELD_FOR_ISOLATION,
            'Field for the isolation values',
            None,
            self.INPUT,
            QgsProcessingParameterField.Numeric)
        )
        
        # We add a feature sink in which to store our processed features 
        
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Discrete Isolation')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # Here is where the processing itself takes place.

        # Retrieve the feature source and sink.
        
        source = self.parameterAsSource(parameters, self.INPUT, context)
        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT,
                context, source.fields(), source.wkbType(), source.sourceCrs())
                
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        if QgsWkbTypes.isMultiType(source.wkbType()):
            raise QgsProcessingException(self.tr('Input layer is a MultiPoint layer - first convert to single points before using this algorithm.'))
                
                
        max_isolation = self.parameterAsInt(parameters, self.MAX_ISOLATION, context)
        isolation_value_field = self.parameterAsString(parameters, self.ISOLATION_VALUE_FIELD, context)
        field_for_isolation = self.parameterAsString(parameters, self.FIELD_FOR_ISOLATION, context)
        
        # init distance measuring
        distance = QgsDistanceArea()
        distance.setSourceCrs(source.sourceCrs(), context.transformContext())
        distance.setEllipsoid(context.ellipsoid())
                
        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()
        
        
        for current, feature in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            
            # if attribute is not NULL calculate distance
            if feature.attribute(isolation_value_field):
            
                # reset distance and iteration over features
                isolation_distance = max_isolation
                all_features = source.getFeatures()
                
                # go over all features and search for higher values
                for a_feature in all_features:
                    
                    a = a_feature.attribute(isolation_value_field)
                    f = feature.attribute(isolation_value_field)

                    if f < a :
                        # in case of a higher values calculate distance
                        a_distance = distance.measureLine(feature.geometry().asPoint(),a_feature.geometry().asPoint())
                        # if distance lower than maximum distance use the lower distance and go on
                        if a_distance < isolation_distance:
                            isolation_distance = a_distance
                        
                
                # save isolation distance into attribute table  
                feature[field_for_isolation] = isolation_distance 
                
            # if attribute is NULL set distance 0
            else:
                feature[field_for_isolation] = 0
            
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
        return 'Discrete Isolation'

    def displayName(self):
        """
        Returns the translated algorithm name
        """
        return 'Discrete Isolation' 

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
        return os.path.dirname(__file__) + '/discrete_isolation_icon.png'
        
    def shortHelpString(self):
        file = os.path.dirname(__file__) + '/discrete_isolation.help'
        if not os.path.exists(file):
            return ''
        with open(file) as helpfile:
            help = helpfile.read()
        return help        

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return DiscreteIsolationAlgorithm()