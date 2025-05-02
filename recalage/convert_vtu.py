import vtk

reader = vtk.vtkXMLUnstructuredGridReader()
reader.SetFileName("Stokes.vtu")
reader.Update()
ugrid = reader.GetOutput()

resampler = vtk.vtkResampleToImage()
resampler.SetInputData(ugrid)
resampler.SetSamplingDimensions(128, 128, 128)
resampler.SetUseInputBounds(True)
resampler.Update()

writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName("Stokes_resampled.vti")
writer.SetInputData(resampler.GetOutput())
writer.Write()
print("Resampling complete. Output saved as Stokes_resampled.vti.")