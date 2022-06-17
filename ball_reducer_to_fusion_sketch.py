#
# inspired by https://github.com/Tomato1107/Cycloidal-Drive-Animation
# 
# 

from posixpath import split
import adsk.core, adsk.fusion, adsk.cam, traceback, math
import sys, os
packagepath = os.path.join(os.path.dirname(sys.argv[0]), 'Lib/site-packages/')
if packagepath not in sys.path:
    sys.path.append(packagepath)



def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        install_numpy = sys.path[0] +'\Python\python.exe -m pip install numpy'
        try:
            import numpy as np
        except:
            ui.messageBox('failed to install numpy\n{}'.format(traceback.format_exc()))
        #ui.messageBox('Hello script')       
        design = app.activeProduct
        # Get the root component of the active design.       
        rootComp = design.rootComponent     
        
        ###########################################################################################################################
        #
        #    Parameters 
        #
        # fusion requires cm as units
        Dia = 6 #Diameter of the pin circle                
        #R = Dia/2 # Radius of the toro        
        #E = 0.3 # Eccentricity of input shaft        
        #N = 19 # Number of rollers        

        Rr = 0.3 # Radius of the rollers
        n = 10 # num rollers
        e = .1 # eccentricity
        d = Rr * 2 # roller diameter
        shaft_radius = .4

        # unlikely you need to edit this
        splinePoints = (n -1) * 20
        

        

        ########################################################################################################################################

        # non edit params
        t = np.linspace(0, 2*np.pi, splinePoints)
        RD=Dia/2 # ring radius
        rd=d/2  # roller radius same as Rr
        
        # Create a new sketch on the xy plane.       
        sketches = rootComp.sketches       
        xyPlane = rootComp.xYConstructionPlane        
        

        #draw balls
        # draw ball
        ball_sketch = sketches.add(xyPlane)
        ball_points = adsk.core.ObjectCollection.create() 
        circles = ball_sketch.sketchCurves.sketchCircles
        for i in range(int(n)): 
            circleA = circles.addByCenterRadius(adsk.core.Point3D.create(RD*math.cos(2*i*math.pi/n)+e,RD*math.sin(2*i*math.pi/n),0),rd)

        #######################################################################################################################################

        #  Eccentric moving disk

        eccentric_sketch = sketches.add(xyPlane)

        # Create an object collection for the points.        
        points = adsk.core.ObjectCollection.create()              


        # draw a shaft circle
        circles = eccentric_sketch.sketchCurves.sketchCircles
        
        # we shift the first sketch items 2e to the right, this this moving eccentric disk
        eccentric_shaft = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), shaft_radius)
        center = circles.addByCenterRadius( adsk.core.Point3D.create((2 * e), 0,0),0.1)

        # moving eccentric inner curve
        # ehypocycloidA
        eccentric_points = adsk.core.ObjectCollection.create()

        rc = (n-1)*(RD/n)
        rm = (RD/n) # 

        #  xa,ya is the ball path from the ball center
        xa = (rc+rm)*np.cos(t)-e*np.cos((rc+rm)/rm*t)
        ya = (rc+rm)*np.sin(t)-e*np.sin((rc+rm)/rm*t)

        dxa = (rc+rm)*(-np.sin(t)+(e/rm)*np.sin((rc+rm)/rm*t))
        dya = (rc+rm)*(np.cos(t)-(e/rm)*np.cos((rc+rm)/rm*t))
        xCoord = xa + rd/np.sqrt(dxa**2 + dya**2)*(-dya) 
        yCoord = ya + rd/np.sqrt(dxa**2 + dya**2)*dxa 

        for i in range(splinePoints):
            # offset X coordinates by eccentric radius
            x = xCoord[i] + 2* e
            eccentric_points.add(adsk.core.Point3D.create(x,yCoord[i],0))

        id_curve  = eccentric_sketch.sketchCurves.sketchFittedSplines.add(eccentric_points)
        id_curve.isConstruction = True


        # moving eccentric  outer
        # ehypocycloidE

        #new shape
        eccentric_points = adsk.core.ObjectCollection.create()

        xCoord = xa - rd/np.sqrt(dxa**2 + dya**2)*(-dya) 
        yCoord = ya - rd/np.sqrt(dxa**2 + dya**2)*dxa

        for i in range(splinePoints):
            x = xCoord[i] + 2* e
            eccentric_points.add(adsk.core.Point3D.create(x,yCoord[i],0))

        od_curve = eccentric_sketch.sketchCurves.sketchFittedSplines.add(eccentric_points)
        od_curve.isConstruction = True


        # center line of eccentric ball path
        eccentric_points = adsk.core.ObjectCollection.create()

        xCoord = xa 
        yCoord = ya 

        for i in range(splinePoints):
            x = xCoord[i] + 2* e
            eccentric_points.add(adsk.core.Point3D.create(x,yCoord[i],0))

        eccentric_sketch.sketchCurves.sketchFittedSplines.add(eccentric_points)

        ########################################################################################################################################
        #
        #           Fixed Disk curves
        #
        ##################################
        #  Add fixed disk id
        # ehypocycloidD
        fixed_sketch = sketches.add(xyPlane)
        circles = fixed_sketch.sketchCurves.sketchCircles
        circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), shaft_radius)
        # new shape
        fixed_points = adsk.core.ObjectCollection.create()

        rc = (n+1)*(RD/n)
        rm = (RD/n)
        xa = (rc-rm)*np.cos(t)+e*np.cos((rc-rm)/rm*t)
        ya = (rc-rm)*np.sin(t)-e*np.sin((rc-rm)/rm*t)

        dxa = (rc-rm)*(-np.sin(t)-(e/rm)*np.sin((rc-rm)/rm*t))
        dya = (rc-rm)*(np.cos(t)-(e/rm)*np.cos((rc-rm)/rm*t))

        xCoord = xa - rd/np.sqrt(dxa**2 + dya**2)*(-dya) 
        yCoord = ya - rd/np.sqrt(dxa**2 + dya**2)*dxa


        for i in range(splinePoints):
            fixed_points.add(adsk.core.Point3D.create(xCoord[i],yCoord[i],0))

        id_curve = fixed_sketch.sketchCurves.sketchFittedSplines.add(fixed_points)
        id_curve.isConstruction = True
        
        ##################################
        #  Add fixed disk  od
        # ehypocycloidF
        fixed_points = adsk.core.ObjectCollection.create()
        i = 0

        xCoord = xa + rd/np.sqrt(dxa**2 + dya**2)*(-dya) 
        yCoord = ya + rd/np.sqrt(dxa**2 + dya**2)*dxa
        for i in range(splinePoints):
            fixed_points.add(adsk.core.Point3D.create(xCoord[i],yCoord[i],0))

        od_curve = fixed_sketch.sketchCurves.sketchFittedSplines.add(fixed_points)
        od_curve.isConstruction = True

        ###################################
        # add ball center path
        fixed_center_points = adsk.core.ObjectCollection.create()

        for i in range(splinePoints):
            #fixed_points.add(adsk.core.Point3d.create(xa[i],ya[i],0 ))
            fixed_center_points.add(adsk.core.Point3D.create(xa[i],ya[i],0))

        fixed_sketch.sketchCurves.sketchFittedSplines.add(fixed_center_points)
            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
