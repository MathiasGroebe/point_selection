# Point selection algorithms

QGIS-Plugin for making different point selection algorithms available:

 - Discrete isolation (Gröbe)
 - [Functional importance](http://imagico.de/map/osm_populated_en.php) (Hormann)
 - [Label grid](https://github.com/mapbox/postgis-vt-util/blob/master/src/LabelGrid.sql) (MapBox)
 
These QGIS tools can help to identify local minimal and maximal in a point data set. This can be useful for cartographic generalization or analysis. While the Discrete isolation and the Functional importance not depending on the map projection, the Label grid relies on the point data's projection.
