import vtk

# A function to observer the progress of the Decimator
def ProgressCommand(sender,event=""):
  if event == "ProgressEvent":
    print sender.GetProgress()
  elif event == "StartEvent":
    print "Starting "+sender.GetClassName()
  elif event == "EndEvent":
    print "Finishing "+sender.GetClassName()

ren1 = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren1)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

renWin.SetSize( 300, 300 )

# Quadric definition
quadric = vtk.vtkQuadric()
quadric.SetCoefficients(.5,1,.2,0,.1,0,0,.2,0,0)

sample = vtk.vtkSampleFunction()
sample.SetSampleDimensions(50,50,50)
sample.SetImplicitFunction(quadric)

# Create five surfaces F(x,y,z) = constant between range specified
contours = vtk.vtkContourFilter()
contours.SetInputConnection(sample.GetOutputPort())
contours.GenerateValues(5, 0.0, 1.2)
#contours.Update()

deci = vtk.vtkDecimatePro()
deci.SetInputConnection(contours.GetOutputPort())
deci.SetTargetReduction(0.9)
deci.PreserveTopologyOn()

smooth = vtk.vtkSmoothPolyDataFilter()
smooth.SetInputConnection(deci.GetOutputPort())
smooth.SetNumberOfIterations(25)

normals = vtk.vtkPolyDataNormals()
normals.SetInputConnection(smooth.GetOutputPort())

contMapper = vtk.vtkPolyDataMapper()
contMapper.SetInputConnection(normals.GetOutputPort())
contMapper.SetScalarRange(0.0, 1.2)

contActor = vtk.vtkActor()
contActor.SetMapper(contMapper)

# Create outline
outline = vtk.vtkOutlineFilter()
outline.SetInputConnection(sample.GetOutputPort())

outlineMapper = vtk.vtkPolyDataMapper()
outlineMapper.SetInputConnection(outline.GetOutputPort())

outlineActor = vtk.vtkActor()
outlineActor.SetMapper(outlineMapper)
outlineActor.GetProperty().SetColor(0,0,0)

ren1.SetBackground(1,1,1)
ren1.AddActor(contActor)
ren1.AddActor(outlineActor)


# Add observers here
deci.AddObserver( "ProgressEvent", ProgressCommand )
deci.AddObserver( "StartEvent", ProgressCommand )
deci.AddObserver( "EndEvent", ProgressCommand )
contours.AddObserver( "StartEvent", ProgressCommand )
contours.AddObserver( "EndEvent", ProgressCommand )
normals.AddObserver( "StartEvent", ProgressCommand )
normals.AddObserver( "EndEvent", ProgressCommand )

# interact with data
iren.Initialize()
iren.Start()

