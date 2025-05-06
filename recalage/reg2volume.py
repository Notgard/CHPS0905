# --------------------------------------------------
# Registration of 2 MRI volumes using elastix. 
#
#       
#
# Robert Marti 2021
# robert.marti@udg.edu
# 
# (fast2) robert@mariecurie:~/src/elastix$ python reg2volumes.py --non_rigid 0 --fixed_image /mnt/mia_images/wholebody/reg_ACF/ACF_26_221.nii.gz --moving_imag
# /mnt/mia_images/wholebody/reg_ACF/ACF_26_321.nii.gz --output_image ./affine_ACF_26_321.nii.gz --output_folder res_affine_mask/ --fixed_mask  /mnt/mia_images/w
# │holebody/reg_ACF/ACF_26_221_labels.nii.gz  --moving_mask  /mnt/mia_images/wholebody/reg_ACF/ACF_26_321_labels.nii.gz
# --------------------------------------------------

import os
import argparse
import time
import SimpleITK as sitk



CURRENT_FOLDER = os.path.dirname(os.path.realpath(__file__))

if __name__ == "__main__":

    # Parse input options
    parser = argparse.ArgumentParser(
        description="Volume registration using elastix")
    parser.add_argument('--non_rigid',
                        action='store',
                        required=True,
                        help='Perform (1) or not (0) non-rigid registration (mandatory)')
    parser.add_argument('--fixed_image',
                        action='store',
                        required=True,
                        help='Input FIXED volume file  (mandatory)')
    parser.add_argument('--moving_image',
                        action='store',
                        required=True,
                        help='Input MOVING volume file  (mandatory)')
    parser.add_argument('--output_image',
                        action = 'store',
                        required=True,
                        help='output transformed moving image filename (mandatory)')
    parser.add_argument('--output_folder',
                        action = 'store',
                        required=True,
                        help='output folder (mandatory)')

    parser.add_argument('--fixed_mask',
                        action = 'store',
                        required=False,
                        help='fixed_mask (optional)')

    parser.add_argument('--moving_mask',
                        action = 'store',
                        required=False,
                        help='moving_mask (optional)')
    
    
    opt = parser.parse_args()
    
    fixed_fn = opt.fixed_image
    moving_fn = opt.moving_image    
    output_fn = opt.output_image
    output_fd = opt.output_folder

    if (opt.fixed_mask is not None) and (opt.moving_mask is not None):
        moving_mask_fn = opt.moving_mask
        fixed_mask_fn = opt.fixed_mask
        using_masks = True
    else: using_masks = False

    if (opt.non_rigid == '1'): do_non_rigid = True
    else: do_non_rigid = False
    print ("Files: ", fixed_fn, moving_fn,output_fn)
    print ("Doing non-rigid: ",do_non_rigid)

    fixed_im = sitk.ReadImage(fixed_fn)
    moving_im = sitk.ReadImage(moving_fn)
    # set same origins & spacings
    f_org = fixed_im.GetOrigin()   
    m_org = moving_im.GetOrigin()
    f_sp = fixed_im.GetSpacing()
    m_sp = moving_im.GetSpacing()

    if (using_masks):
        fixed_msk = sitk.ReadImage(fixed_mask_fn)
        moving_msk = sitk.ReadImage(moving_mask_fn)
        fixed_msk.SetSpacing(f_sp)
        moving_msk.SetSpacing(m_sp)
        fixed_msk.SetOrigin(f_org)
        moving_msk.SetOrigin(m_org)


    print(fixed_im.GetPixelIDTypeAsString())
    fixed_pixelID = fixed_im.GetPixelID()

    # # fixed_im.SetOrigin (f_sp)
    # moving_im.SetOrigin (f_org)
    # moving_im.SetSpacing(f_sp)
    # moving_im.CopyInformation(fixed_im)
    moving_r_im = sitk.Resample(moving_im, fixed_im, sitk.Transform(), sitk.sitkNearestNeighbor, 0.0, fixed_im.GetPixelID())

        
    # diff_fm = sitk.AbsoluteValueDifference(fixed_im,moving_im)
    diff_fm = sitk.Subtract(fixed_im,moving_r_im)

    sitk.WriteImage(diff_fm, output_fd+"diff_before.nii.gz")

    # undo the modifications.
    # moving_im.SetOrigin (m_org)
    # moving_im.SetSpacing(m_sp)

    elastixImageFilter = sitk.ElastixImageFilter()
    elastixImageFilter.SetFixedImage(fixed_im)
    elastixImageFilter.SetMovingImage(moving_im)      
        
    parameterMapVector = sitk.VectorOfParameterMap()
    # parameterMapVector.append(sitk.GetDefaultParameterMap("affine"))
    parameterMapVector.append(sitk.GetDefaultParameterMap("rigid"))
    
    if (do_non_rigid):
        parameterMapVector.append(sitk.GetDefaultParameterMap("bspline"))


    elastixImageFilter.SetParameterMap(parameterMapVector)
    # elastixImageFilter.SetParameter("FinalGridSpacingInPhysicalUnits",'100')  #"50.0 50.0 50.0")#"8.0 8.0 8.0")  (FinalGridSpacingInPhysicalUnits 8)
    # elastixImageFilter.SetParameter("GridSpacingSchedule", ['4.0','2.0','1.0']) #  (GridSpacingSchedule 2.80322 1.9881 1.41 1)
    # elastixImageFilter.SetParameter("NumberOfResolutions", '3') #  (GridSpacingSchedule 2.80322 1.9881 1.41 1)
    if (do_non_rigid): 
        elastixImageFilter.SetParameter("FinalGridSpacingInPhysicalUnits",'5')  #"50.0 50.0 50.0")#"8.0 8.0 8.0")  (FinalGridSpacingInPhysicalUnits 8)
        # elastixImageFilter.SetParameter("GridSpacingSchedule", ['8.0','4.0','2.0','1.0']) #  (GridSpacingSchedule 2.80322 1.9881 1.41 1)
        # elastixImageFilter.SetParameter("NumberOfResolutions", '4') #  (GridSpacingSchedule 2.80322 1.9881 1.41 1)
        elastixImageFilter.SetParameter("GridSpacingSchedule", ['8.0','4.0','2.0']) #  (GridSpacingSchedule 2.80322 1.9881 1.41 1)
        elastixImageFilter.SetParameter("NumberOfResolutions", '3') #  (GridSpacingSchedule 2.80322 1.9881 1.41 1)
    elastixImageFilter.SetParameter("MaximumNumberOfIterations",'5000') # max number of iterations was 255
    elastixImageFilter.SetParameter("NumberOfSpatialSamples",'8192') # was 2048
    elastixImageFilter.SetOutputDirectory(output_fd)
    
    if (using_masks):
        print('using Masks')
        elastixImageFilter.SetFixedMask(fixed_msk)
        # elastixImageFilter.SetMovingMask(moving_msk)
        # elastixImageFilter.SetParameter("NumberOfSpatialSamples",'8192') # was 2048
        elastixImageFilter.SetParameter("MaximumNumberOfSamplingAttempts",'50') # was 8 by default
        elastixImageFilter.SetParameter("RequiredRatioOfValidSamples",'0.01') # was 0.25  by default
        elastixImageFilter.SetParameter("ImageSampler",'RandomSparseMask') # was 0.25  by default
         
    elastixImageFilter.PrintParameterMap()

    input('press to execute')
    elastixImageFilter.Execute()  
   
    transf_moving = elastixImageFilter.GetResultImage()
    sitk.WriteImage(transf_moving, output_fd+output_fn)
     
    transformixImageFilter = sitk.TransformixImageFilter()
    transformixImageFilter.SetTransformParameterMap(elastixImageFilter.GetTransformParameterMap())
    transformixImageFilter.ComputeDeformationFieldOn()
    transformixImageFilter.LogToConsoleOn()
    transformixImageFilter.ComputeDeformationFieldOn()
    transformixImageFilter.ComputeDeterminantOfSpatialJacobianOn()
    # transformixImageFilter.ComputeSpatialJacobianOn() no need for jacobian (too much space)
    transformixImageFilter.SetOutputDirectory(output_fd)
    transformixImageFilter.SetMovingImage(moving_im)
    transformixImageFilter.Execute()
    deformationField = transformixImageFilter.GetDeformationField()


    # print(fixed_im.GetPixelIDTypeAsString())
    # print(transf_moving.GetPixelIDTypeAsString())
    transf_moving_cast = sitk.Cast(transf_moving,fixed_pixelID)
   
    # diff_after = sitk.AbsoluteValueDifference(fixed_im,transf_moving_cast)
    diff_after = sitk.Subtract(fixed_im,transf_moving_cast)
    sitk.WriteImage(diff_after, output_fd+"diff_after.nii.gz")

    
    