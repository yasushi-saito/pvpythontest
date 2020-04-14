#!/usr/bin/env python

# This example demonstrates how to use the vtkPlaneWidget to probe a
# dataset and then generate contours on the probed data.

import vtk

# Create a mace out of filters.
sphere = vtk.vtkSphereSource()
cone = vtk.vtkConeSource()
glyph = vtk.vtkGlyph3D()
glyph.SetInputConnection(sphere.GetOutputPort())
glyph.SetSourceConnection(cone.GetOutputPort())
glyph.SetVectorModeToUseNormal()
glyph.SetScaleModeToScaleByVector()
glyph.SetScaleFactor(0.25)

# The sphere and spikes are appended into a single polydata.
# This just makes things simpler to manage.
apd = vtk.vtkAppendPolyData()
apd.AddInputConnection(glyph.GetOutputPort())
apd.AddInputConnection(sphere.GetOutputPort())

maceMapper = vtk.vtkPolyDataMapper()
maceMapper.SetInputConnection(apd.GetOutputPort())

maceActor = vtk.vtkActor()
maceActor.SetMapper(maceMapper)
maceActor.VisibilityOn()


# Axes
outline = vtk.vtkOutlineFilter()
outline.SetInputConnection(apd.GetOutputPort())
mapOutline = vtk.vtkPolyDataMapper()
mapOutline.SetInputConnection(outline.GetOutputPort())
outlineActor = vtk.vtkActor()
outlineActor.SetMapper(mapOutline)
outlineActor.GetProperty().SetColor(0, 0, 0)

# This portion of the code clips the mace with the vtkPlanes
# implicit function. The clipped region is colored green.
plane = vtk.vtkPlane()
clipper = vtk.vtkClipPolyData()
clipper.SetInputConnection(apd.GetOutputPort())
clipper.SetClipFunction(plane)
clipper.InsideOutOn()

selectMapper = vtk.vtkPolyDataMapper()
selectMapper.SetInputConnection(clipper.GetOutputPort())

selectActor = vtk.vtkActor()
selectActor.SetMapper(selectMapper)
selectActor.GetProperty().SetColor(0, 1, 1)
selectActor.VisibilityOff()
selectActor.SetScale(1.01, 1.01, 1.01)

# Create the RenderWindow, Renderer and both Actors
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# The callback function
def myCallback(obj, event):
    global plane, selectActor, planeRep
    planeRep.GetPlane(plane)
    print("MYCALLBACK", type(obj), type(event), event)
    selectActor.VisibilityOn()

# Associate the line widget with the interactor
planeRep = vtk.vtkImplicitPlaneRepresentation()
planeRep.SetPlaceFactor(1.0)
glyph.Update()
bounds = glyph.GetOutput().GetBounds()
#bounds = [0,0,0, 1,1,1]
origin = [(bounds[0]+bounds[1])/2.0,
          (bounds[2]+bounds[3])/2.0,
          (bounds[4]+bounds[5])/2.0]
print("BOUNDS", bounds, "origin", origin)
planeRep.PlaceWidget(bounds)
if False:
    planeRep.SetOrigin(origin)

planeWidget = vtk.vtkImplicitPlaneWidget2()
planeWidget.SetInteractor(iren)
planeWidget.SetRepresentation(planeRep)
#planeWidget.SetInputConnection(glyph.GetOutputPort())
planeWidget.AddObserver("InteractionEvent", myCallback)

ren.AddActor(maceActor)
ren.AddActor(selectActor)
ren.AddActor(outlineActor)

axes = vtk.vtkCubeAxesActor2D()
axes.SetInputConnection(apd.GetOutputPort())
axes.SetCamera(ren.GetActiveCamera())
axes.SetLabelFormat("%6.4g")
axes.SetFlyModeToOuterEdges()
axes.SetFontFactor(0.8)
tprop = vtk.vtkTextProperty()
tprop.SetColor(1, 1, 1)
tprop.ShadowOn()
axes.SetAxisTitleTextProperty(tprop)
axes.SetAxisLabelTextProperty(tprop)
ren.AddActor(axes)

# Add the actors to the renderer, set the background and size
ren.SetBackground(1, 1, 1)
renWin.SetSize(300, 300)
ren.SetBackground(0.1, 0.2, 0.4)

# Start interaction.
iren.Initialize()
renWin.Render()
iren.Start()
