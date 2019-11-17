# DART bugs
This section aims at listing the bugs that were noticed with DART, solved or not.

## current bugs
In parenthesis is the DART version on which it has been observed.

* (v1083) pytools4dart executed on headless server (i.e. without display) leads to an error:

    `Exception in thread "main" java.awt.AWTError: Can't connect to X11 window server using ':0' as the value of the DISPLAY variable.`
     
     The solution is to activate awt headless:
     
     `ls ~/DART/tools/linux/*.sh | xargs sed -i 's#$DART_HOME/bin/jre/bin/java#$DART_HOME/bin/jre/bin/java -Djava.awt.headless=true#g'`
     

 

 
* (v1083) column order is important in database imports. 
As an example, 2D-LAM_xxx.txt must have columns 'wavelength', 'reflectance', 'direct transmittance', 'diffuse transmittance' 
in this order, otherwise the data is wrongly interpreted, and makes wrong simulations in flux-tracking and lidar,
 although not sending any warning or error at simulation.

* (v1083) DAO not working:
    "C'est probablement que le nouveau format n'est pas activé (la scene d'exemple fonctionne chez moi avec la 1118). 2 solutions:
    1) en python: c.f. manuel de la DAO, section 1.2 (en bas de la 1ère page) => dao.Mockup.enableNewMaketFormat(DART_HOME, enable=True)
    2) à la main: créer un fichier vide "dao.nfm" dans le répertoire DART_HOME"

* (v1083) plots converted to triangles consumes enormous RAM at mockup creation (dart-maket)
 

## v1121
### Fix
* memory leak in DART Lidar: overloads memory for a simulation of 10e6 pulses (with scene of 7e6 triangles).
  **should be fixed since february 2019, checked on v1121**

## v1111
### Changes
* obj group name order changed from HashMap keySet to alphabetic order

