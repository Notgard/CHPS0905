import vtk

reader = vtk.vtkXMLUnstructuredGridReader()
reader.SetFileName("VTK_Files/Stokes.vtu")

writer = vtk.vtkUnstructuredGridWriter()
writer.SetInputConnection(reader.GetOutputPort(0))
writer.SetFileName("output.vtk")  # VTK unstructured grid file
writer.Write()
