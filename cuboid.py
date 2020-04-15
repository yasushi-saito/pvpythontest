#!/usr/bin/env python

# This example demonstrates how to use the vtkPlaneWidget to probe a
# dataset and then generate contours on the probed data.

import vtk

# The sphere and spikes are appended into a single polydata.
# This just makes things simpler to manage.
# apd = vtk.vtkUnstructuredGridReader()
apd = vtk.vtkRectilinearGridReader()
apd.SetFileName("/home/saito/paraview/solution_40.vtk")
apd.SetScalarsName("Pressure")
glyph = apd
apd.Update()


def PrintMetadata(name, obj):
    print(
        f"{name}: #inputs=",
        apd.GetNumberOfInputPorts(),
        "#outputs=",
        apd.GetNumberOfOutputPorts(),
        "header:",
        apd.GetHeader(),
        "filetype:",
        apd.GetFileType(),
    )

    i = 0
    while True:
        array = apd.GetOutput().GetCellData().GetAbstractArray(i)
        print(f"array {i}: {array}")
        if not array:
            break
        i += 1

    # print(f"{name}: pointdata: ", apd.GetOutput().GetPointData())
    # print(f"{name}: celldata: ", apd.GetOutput().GetCellData())
    print(
        f"{name}: celldata #arrays: ", apd.GetOutput().GetCellData().GetNumberOfArrays()
    )
    print(f"{name}: celldata (vector): ", apd.GetOutput().GetCellData().GetVectors())

    print(
        f"{name}: #scalars=",
        apd.GetNumberOfScalarsInFile(),
        "#vectors=",
        apd.GetNumberOfVectorsInFile(),
    )
    for i in range(0, apd.GetNumberOfScalarsInFile()):
        name = apd.GetScalarsNameInFile(i)
        print("Scalar: ", i, name)

    for i in range(0, apd.GetNumberOfVectorsInFile()):
        name = apd.GetVectorsNameInFile(i)
        print("Vec: ", i, name)


if True:
    # Get the information
    print(
        "Info:", apd.GetInformation(), "#keys=", apd.GetInformation().GetNumberOfKeys()
    )
    iter = vtk.vtkInformationIterator()
    iter.SetInformation(apd.GetInformation())
    iter.InitTraversal()
    while True:
        if iter.IsDoneWithTraversal():
            break
        print("KEY: ", iter.GetCurrentKey())
        iter.GoToNextItem()

# PrintMetadata("apd", apd)

geoFilter = vtk.vtkGeometryFilter()
geoFilter.SetInputConnection(apd.GetOutputPort())
PrintMetadata("geo", geoFilter)

#thresh = vtk.vtkThreshold()
#thresh.SetInputConnection(apd.GetOutputPort())
#thresh.ThresholdBetween(-10000, 10000)
#thresh.SetAttributeModeToUseCellData()

maceMapper = vtk.vtkPolyDataMapper()
maceMapper.SetInputConnection(geoFilter.GetOutputPort())
geoFilter.Update()
pressure = geoFilter.GetOutput().GetCellData().GetScalars("Pressure")
pressureRange = pressure.GetRange()
print("GEOGEO", pressure, "range=", pressure.GetRange())

#maceMapper.SetInputArrayToProcess(1,0,0,0, "Pressure")
maceMapper.SetScalarModeToUseCellData()
maceMapper.SetScalarRange(pressureRange)
colorLookupTable = vtk.vtkLookupTable()
#colorLookupTable.SetTableRange(100.30, 100.37)
colorLookupTable.SetHueRange(0.3, 0.8)
colorLookupTable.Build()
maceMapper.SetLookupTable(colorLookupTable)

maceActor = vtk.vtkActor()
maceActor.SetMapper(maceMapper)
maceActor.VisibilityOn()
maceActor.GetProperty().EdgeVisibilityOn()

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
print("BOUNDSX", bounds)
origin = [
    (bounds[0] + bounds[1]) / 2.0,
    (bounds[2] + bounds[3]) / 2.0,
    (bounds[4] + bounds[5]) / 2.0,
]
print("BOUNDS", bounds, "origin", origin)
planeRep.PlaceWidget(bounds)
if True:
    planeRep.SetOrigin(origin)

planeWidget = vtk.vtkImplicitPlaneWidget2()
planeWidget.SetInteractor(iren)
planeWidget.SetRepresentation(planeRep)
# planeWidget.SetInputConnection(glyph.GetOutputPort())
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
