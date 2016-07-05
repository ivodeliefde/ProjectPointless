
# Project Pointless

- [What is Project Pointless?](https://github.com/ivodeliefde/ProjectPointless#1-what-is-project-pointless)
- [How does it work? ](https://github.com/ivodeliefde/ProjectPointless#2-how-does-it-work)
- [How to use the Pointless application](https://github.com/ivodeliefde/ProjectPointless#3-how-to-use-the-pointless-application)
- [Emtpy Space Octree](https://github.com/ivodeliefde/ProjectPointless#4-emtpy-space-octree)
- [Pointlessconverter](https://github.com/ivodeliefde/ProjectPointless#5-pointless-converter)
- [Example Use Cases](https://github.com/ivodeliefde/ProjectPointless#6-example-use-cases)
- [Contact](https://github.com/ivodeliefde/ProjectPointless#7-contact)

## 1. What is Project Pointless?
Project pointless is an open source project about calculating the empty space in (indoor) point clouds. Having the empty space allows for a number of useful applications, such as: route finding, better visualisation and object fitting (can an object fit through a space?).
The project is started by master students of Geomatics TU Delft as project on the use of explorative point clouds. This means that the applications are not made to use geometric models derived from point clouds, because the full richness and details of captured data will then be lost (Verbree & Oosterom 2014). Instead Project Pointless uses the point cloud itself as input for applications without creating any geometric models of it first. This way the full richness of the point cloud can be used. 

For more info go to http://projectpointless.bitballoon.com or follow us on twitter: https://twitter.com/ProjPointless 

## 2. How does it work? 
Project pointless exists of two parts: the pointless converter and the pointless viewer. The converter is a flask application that runs in the browser and takes a .las file as input together with other parameters like the user's PostgreSQL username and password. The point cloud is being scaled and translated first and then stored in the database in an special kind of Octree structure (see chapter on Octrees). The Pointless Viewer is another flask application that let's you log in to your PostgreSQL database and view the Pointcloud as well as the empty space using WebGL in the browser. 

## 3. How to use the Pointless application

### 3.1 Requirements
The application has a number of dependencies, which are required to run on your computer in order to use it:
- [PostgresQL](http://www.postgresql.org/)
- [Python version 2.7](https://docs.python.org/2/)

With the following python packages:
- Flask
- Flask-SQLAlchemy
- Liblas
- CStringIO
- Psycopg2
- werkzeug
- asciitable

Most of these packages can be installed using pip or easyinstall. They can also be downloaded [from this website](http://www.lfd.uci.edu/~gohlke/pythonlibs/).

The Pointless application was created and tested with the point clouds below. However, it takes all point cloud files in the [.las file format](http://www.asprs.org/Committee-General/LASer-LAS-File-Format-Exchange-Activities.html). The point clouds used to test this application will soon be made available as open data!

![](https://github.com/ivodeliefde/ProjectPointless/blob/master/images/PointcloudBBOX_withEDL.PNG)

![](https://github.com/ivodeliefde/ProjectPointless/blob/master/images/BouwpubC10.PNG)

*note: these pictures were taken using [Cloudcompare](http://www.danielgm.net/cc/) and the [Potree](https://github.com/potree/potree) point cloud renderer*


### 3.2 Pointless Converter
To start the point cloud converter you should open the command line go to the folder where project pointless is stored. Then run the following command:
```
$ python converterinterface.py
```
A localhost is now running and you can access the application in the browser by going to 'http://localhost:5000' in the addressbar. Now you should be seeing the following screen:

![](https://github.com/ivodeliefde/ProjectPointless/blob/master/images/converterInterface.PNG)

Browse and select your pointcloud, choose a name for the new database to be created and fill out the username and password of your PostgreSQL user. The dropdown menu at the bottom allows you to set the maximum level of the octree. By default the maximum level is set to 8. Press submit to start the conversion. In the command line you can find print statements indicating the progress of the conversion. On a high performance laptop the conversion of a point cloud of 2.3 million points took rougly 2 minutes. 

After the conversion has finished the browser will automatically be redirected to the Pointless viewer. If you open PGadmin the new database is there under the name that was filled out in the submit form. It consists of 2 tables:
- pointcloud, this table stores the entire point cloud and columns for:
  - materialpath (the location code of the point in the octree)
  - x value
  - y value
  - z value
  - red value
  - green value
  - blue value
- emptyspace, this table contains the empty leaf nodes of the octree and has columns for:
  - materialpath (the location code of the point in the octree)
  - x of lower left corner 
  - y of lower left corner 
  - z of lower left corner
  - size: the size of a leaf node depends on its location in the octree
 
### 3.3 Pointless Viewer
This is a basic viewer to visualize the special Octree structure. To start the point cloud viewer you should open the command line go to the folder where project pointless is stored. Then run the following command:
```
$ python viewerinterface.py
```  
A localhost is now running and you can access the application in the browser by going to 'http://localhost:5000' in the addressbar. Now you should be seeing the following screen:

![](https://github.com/ivodeliefde/ProjectPointless/blob/master/images/viewerInterface.PNG)

Type in the name of the database created using the Pointless converter and enter you PostgreSQL user login credentials. Click on submit to go to the viewer. It can be that the viewer is not directly looking in the right direction. Look around a bit by dragging the cursor and locate the white bounding box. Click on the 'Help' button in the header bar to get more info about the navigation controls. Once you've located the white bounding box click on one of the other buttons in the header bar to view your dataset. Because the current application is not able to render very large amounts of points this viewer cannot load all points (nor all empty leaf nodes) at the same time. This viewer can be used to get a sense of the dataset and for validation purposes. For realistic rendering of large point clouds check out the amazing [Potree](https://github.com/potree/potree). 

The following video shows [the viewer in action](https://www.youtube.com/watch?v=8vbmw6NwByU&feature=youtu.be) (don't forget to enjoy the music!). 

## 4. Emtpy Space Octree
Every point in the point cloud will have one materialized path assigned to it. This materialised path refers to the corresponding leaf node it is located in. This octree structure is thus a linear octree. Materialized paths are built by traversing the tree from root node to leaf node, thereby adding the name of the node where the point is located to a string for every level. This means that every level in the octree will be represented by a single digit in the eventual materialized path. This path shows which steps needs to be followed through the tree from root to leaf node in order to find the leaf node containing a specific point.

<img src="https://github.com/ivodeliefde/ProjectPointless/blob/master/images/Octree.jpg" width="250px"/>

<img src="https://github.com/ivodeliefde/ProjectPointless/blob/master/images/Numbering.jpg" width="250px"/>

## 5. Conversions Methods

### 5.1 Scaling, translation and point snapping 

By translating the point cloud to the origin of the coordinate system and by scaling it so that the domain in every dimension equals 2^n it is possible to identify the voxel in which a point is located by simply truncating the decimals behind comma towards 0.
In python the function int() does exactly this and is therefore a very elegant way of snapping the points from the input point cloud to the grid. 

<img src="https://github.com/ivodeliefde/ProjectPointless/blob/master/images/scaling.jpg" width="250px"/>

### 5.2 Binary masking
Finding the materialised paths is done using a method called binary masking. The location of a cell can be encoded with only 3 bits for every level in the tree: one bit for x, one for y and one for z. The bits are switched on if the coordinate is over half of the domain for the parent node at a particular level. For every level the octree splits another time and therefore three additional digits are added to the materialised path. To store a smaller location code and to make it better understandable the binary values for every split level are converted to decimals number ranging from 0 (000) to 7 (111).  

![](https://github.com/ivodeliefde/ProjectPointless/blob/master/images/binary_masking.jpg) 

## 6. Example Use Cases

### 6.1 Route finding
The A* algorithm was used to compute the shortest path between two points in the point cloud. 
It takes a set of neighbours as input that are determined by the method presented by Vörös (200). This method calculates all potential neighbours of a leaf node: equal sized neighbours within the same octant and outside the same octant, smaller sized neighbours within the same octant and outside the same octant and the larger sized neighbours outside the same octant (larger sized neighbours within the same octant are not possible because they share the same parent node). The set of all potential neighbours are compared with the set of empty space leaf nodes in the database to find all neighbouring empty space leaf nodes. 

A path is defined as the route between the two nodes the points are located in. The A* is an extension of Dijkstra’s algorithm by implementing a heuristic cost to the algorithm. The heuristic cost estimates the cost from the current node to the goal node. The new cost to mark the node with the lowest cost is now: The cost from the start node to the current node (path cost) + the heuristic cost (Nosrati, Masoud, Ronak Karimi, and Hojat Allah Hasanvand 2012). 

<img src="https://github.com/ivodeliefde/ProjectPointless/blob/master/images/route.PNG" width="500px"/>

### 6.2 Volume Calculations
As an additional use case a method has been quickly developed to estimate the volume of a building represented by the point cloud. This method slices the dataset in every dimension and calculates the empty leaf nodes between the minimum and maximum coordinates in every other dimension. The empty space leaf nodes that have been identified in each dimension are stored in a set. The sets for x, y and z are then compared and only leaf nodes that are member of each set are considered to represent the interior volume. This give a rough estimate and works particularly well for buildings with a rectangular shape grammar. Noise has a low influence on this method as well.  

## 7. Contact

Email: i.deliefde@student.tudelft.nl

For more info go to http://projectpointless.bitballoon.com or follow us on twitter: https://twitter.com/ProjPointless 

This project started as a synthesis project by:
- Erik Heeres
- Florian Fichtner
- Ivo de Liefde
- Olivier Rodenberg
- Tom Broersen

The synthesis project is part of the [Geomatics master programme](http://geomatics.tudelft.nl/) at Delft University of Technology.

## Referencess

Nosrati, Masoud, Ronak Karimi, and Hojat Allah Hasanvand, 2012. Investigation of the*(star) search algorithms: Characteristics, methods and approaches. World Applied Programming, pp.251–256.
Verbree, E. & Oosterom, P., 2014. Explorative point clouds maps for immediate use and analysis.
Vörös, J., 2000. A strategy for repetitive neighbor finding in octree representations. Image and vision computing, 18(14), pp.1085–1091.

