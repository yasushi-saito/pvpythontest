#!/usr/bin/env pvpython


# First we include the VTK Python packages that will make available
# all of the VTK commands to Python.
#
import vtk
import time

#
# Next we create an instance of vtkConeSource and set some of its
# properties. The instance of vtkConeSource "cone" is part of a visualization
# pipeline (it is a source process object); it produces data (output type is
# vtkPolyData) which other filters may process.
#

if True:
    part = vtk.vtkSTLReader()
    part.SetFileName("/home/saito/src0/testdata/pug.stl")
    cone = part
else:
    cone = vtk.vtkConeSource()
    cone.SetHeight(3.0)
    cone.SetRadius(1.0)
    cone.SetResolution(10)

#
# In this example we terminate the pipeline with a mapper process object.
# (Intermediate filters such as vtkShrinkPolyData could be inserted in
# between the source and the mapper.)  We create an instance of
# vtkPolyDataMapper to map the polygonal data into graphics primitives. We
# connect the output of the cone source to the input of this mapper.
#
coneMapper = vtk.vtkPolyDataMapper()
coneMapper.SetInputConnection(cone.GetOutputPort())

#
# Create an actor to represent the cone. The actor orchestrates rendering of
# the mapper's graphics primitives. An actor also refers to properties via a
# vtkProperty instance, and includes an internal transformation matrix. We
# set this actor's mapper to be coneMapper which we created above.
#
coneActor = vtk.vtkLODActor()
coneActor.SetMapper(coneMapper)
prop = vtk.vtkProperty()
prop.SetOpacity(0.2)
prop.SetAmbient(0.5)
prop.SetColor(0.1, 0.4, 0.2)
#coneActor.GetProperty().SetOpacity(0.1)
coneActor.SetProperty(prop)

#
# Create the Renderer and assign actors to it. A renderer is like a
# viewport. It is part or all of a window on the screen and it is
# responsible for drawing the actors it has.  We also set the background
# color here
#
ren1 = vtk.vtkRenderer()
ren1.AddActor(coneActor)
ren1.SetBackground(0.1, 0.2, 0.4)

cam1 = ren1.GetActiveCamera()
cam1.Zoom(10)


#
# Finally we create the render window which will show up on the screen
# We put our renderer into the render window using AddRenderer. We also
# set the size to be 300 pixels by 300
#
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren1)
renWin.SetSize(20, 20)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

style = vtk.vtkInteractorStyleTrackballCamera()
iren.SetInteractorStyle(style)

print("INIT")
iren.Initialize()
print("START")
iren.Start()
print("START2")
#
# now we loop over 360 degrees and render the cone each time
#
for i in range(0, 360):
    time.sleep(0.5)

    renWin.Render()
    ren1.GetActiveCamera().Azimuth(10)
