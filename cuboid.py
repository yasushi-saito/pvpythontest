#!/usr/bin/env python

# This example demonstrates how to use the vtkPlaneWidget to probe a
# dataset and then generate contours on the probed data.

import vtk
from typing import Tuple, TypeVar

def print_dataset_metadata(obj):
    print(
        f"{name}: #scalars=",
        obj.GetNumberOfScalarsInFile(),
        "#vectors=",
        obj.GetNumberOfVectorsInFile(),
    )
    for i in range(0, obj.GetNumberOfScalarsInFile()):
        name = obj.GetScalarsNameInFile(i)
        print("Scalar: ", i, name)

    for i in range(0, obj.GetNumberOfVectorsInFile()):
        name = obj.GetVectorsNameInFile(i)
        print("Vec: ", i, name)

def print_metadata(name, obj):
    print(
        f"{name}: #inputs=",
        obj.GetNumberOfInputPorts(),
        "#outputs=",
        obj.GetNumberOfOutputPorts(),
    )

    i = 0
    while True:
        array = obj.GetOutput().GetCellData().GetAbstractArray(i)
        print(f"array {i}: {array}")
        if not array:
            break
        i += 1

    # print(f"{name}: pointdata: ", obj.GetOutput().GetPointData())
    # print(f"{name}: celldata: ", obj.GetOutput().GetCellData())
    print(
        f"{name}: celldata #arrays: ", obj.GetOutput().GetCellData().GetNumberOfArrays()
    )
    print(f"{name}: celldata (vector): ", obj.GetOutput().GetCellData().GetVectors())


def get_information(obj):
    print(
        "Info:", obj.GetInformation(), "#keys=", obj.GetInformation().GetNumberOfKeys()
    )
    iter = vtk.vtkInformationIterator()
    iter.SetInformation(obj.GetInformation())
    iter.InitTraversal()
    while True:
        if iter.IsDoneWithTraversal():
            break
        print("KEY: ", iter.GetCurrentKey())
        iter.GoToNextItem()


# AlgorithmT = TypeVar('AlgortihmT', bound=vtk.vtkAlgorithm)
# def connect(node: vtk.vtkAlgorithm, next: AlgorithmT) -> AlgorithmT:
#     next.SetInputConnection(node.GetOutputPort())
#     return next

def new_geometry_actor(data_source: vtk.vtkDataSet) -> vtk.vtkActor:
    geometry_filter = vtk.vtkGeometryFilter()
    geometry_filter.SetInputConnection(data_source.GetOutputPort())
    geometry_filter.Update()
    pressure_data = geometry_filter.GetOutput().GetCellData().GetScalars("Pressure")
    print_metadata("geo", geometry_filter)
    print("Pressure: range=", pressure_data.GetRange())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(geometry_filter.GetOutputPort())
    mapper.SetScalarModeToUseCellData()
    mapper.SetScalarRange(pressure_data.GetRange())
    color_lookup_table = vtk.vtkLookupTable()
    color_lookup_table.SetHueRange(0.3, 0.8)
    color_lookup_table.Build()
    mapper.SetLookupTable(color_lookup_table)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.VisibilityOn()
    actor.GetProperty().EdgeVisibilityOn()
    return actor

def new_outline_actor(node: vtk.vtkDataSet):
    outline = vtk.vtkOutlineFilter()
    outline.SetInputConnection(node.GetOutputPort())
    mapOutline = vtk.vtkPolyDataMapper()
    mapOutline.SetInputConnection(outline.GetOutputPort())
    outlineActor = vtk.vtkActor()
    outlineActor.SetMapper(mapOutline)
    outlineActor.GetProperty().SetColor(0, 0, 0)
    return outlineActor


def new_implicit_plane_widget(data_source) -> Tuple[vtk.vtkAbstractWidget, vtk.vtkProp]:
    # This portion of the code clips the mace with the vtkPlanes
    # implicit function. The clipped region is colored green.
    select_plane = vtk.vtkPlane()
    clipper = vtk.vtkClipDataSet()
    clipper.SetInputConnection(data_source.GetOutputPort())
    clipper.SetClipFunction(select_plane)
    clipper.InsideOutOn()

    selectMapper = vtk.vtkPolyDataMapper()
    selectMapper.SetInputConnection(clipper.GetOutputPort())

    selectActor = vtk.vtkActor()
    selectActor.SetMapper(selectMapper)
    selectActor.GetProperty().SetColor(0, 1, 1)
    selectActor.VisibilityOff()
    selectActor.SetScale(1.01, 1.01, 1.01)

    # Associate the line widget with the interactor
    planeRep = vtk.vtkImplicitPlaneRepresentation()
    planeRep.SetPlaceFactor(2.0)
    data_source.Update()
    bounds = data_source.GetOutput().GetBounds()
    origin = [
        (bounds[0] + bounds[1]) / 2.0,
        (bounds[2] + bounds[3]) / 2.0,
        (bounds[4] + bounds[5]) / 2.0,
    ]
    planeRep.PlaceWidget(bounds)
    planeRep.SetOrigin(origin)
    planeWidget = vtk.vtkImplicitPlaneWidget2()
    planeWidget.SetRepresentation(planeRep)
    # planeWidget.SetInputConnection(glyph.GetOutputPort())
    def myCallback(obj, event):
        planeRep.GetPlane(select_plane)
        print("MYCALLBACK", type(obj), type(event), event)
        selectActor.VisibilityOn()

    planeWidget.AddObserver("InteractionEvent", myCallback)
    return planeWidget, selectActor

def new_axes_actor(ren: vtk.vtkRenderer, data_source):
    axes = vtk.vtkCubeAxesActor2D()
    axes.SetInputConnection(data_source.GetOutputPort())
    axes.SetCamera(ren.GetActiveCamera())
    axes.SetLabelFormat("%6.4g")
    axes.SetFlyModeToOuterEdges()
    axes.SetFontFactor(0.8)
    tprop = vtk.vtkTextProperty()
    tprop.SetColor(1, 1, 1)
    tprop.ShadowOn()
    axes.SetAxisTitleTextProperty(tprop)
    axes.SetAxisLabelTextProperty(tprop)
    return axes

def main():
    # The sphere and spikes are appended into a single polydata.
    # This just makes things simpler to manage.
    # apd = vtk.vtkUnstructuredGridReader()
    data_source = vtk.vtkRectilinearGridReader()
    data_source.SetFileName("/home/saito/paraview/solution_40.vtk")
    data_source.SetScalarsName("Pressure")


    # Create the RenderWindow, Renderer and both Actors
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    implicit_plane_widget, selected_plane_actor = new_implicit_plane_widget(data_source)
    implicit_plane_widget.SetInteractor(iren)

    ren.AddActor(new_geometry_actor(data_source))
    ren.AddActor(selected_plane_actor)
    ren.AddActor(new_outline_actor(data_source))
    ren.AddActor(new_axes_actor(ren, data_source))

    # Add the actors to the renderer, set the background and size
    ren.SetBackground(1, 1, 1)
    renWin.SetSize(300, 300)
    ren.SetBackground(0.1, 0.2, 0.4)

    # Start interaction.
    iren.Initialize()
    renWin.Render()
    iren.Start()

import trace
tt = trace.Trace()
tt.runfunc(main)
