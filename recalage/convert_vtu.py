import vtk

reader = vtk.vtkXMLUnstructuredGridReader()
reader.SetFileName("VTK_Files/Stokes.vtu")
reader.Update()

resampler = vtk.vtkResampleToImage()
resampler.SetInputData(reader.GetOutput())
resampler.SetSamplingDimensions(128, 128, 128)  # adjust as needed
resampler.SetUseInputBounds(True)
resampler.Update()

writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName("output.vti")  # VTK image data file
writer.SetInputData(resampler.GetOutput())
writer.Write()
