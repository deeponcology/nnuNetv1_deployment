import SimpleITK as sitk
import os
import numpy as np
import subprocess
from pathlib import Path
import tempfile
from data_utils import resample_img, GetROIfromDownsampledSegmentation, FPreductionPancreasMaskEnsamble

def translate_pred_to_reference_scan_from_file(pred, reference_scan_path, transpose=False):
    """
    Compatibility layer for `translate_pred_to_reference_scan`
    - pred_path: path to softmax / binary prediction
    - reference_scan_path: path to SimpleITK image to which the prediction should be resampled and resized
    - out_spacing: spacing to which the reference scan is resampled during preprocessing
    Returns:
    - SimpleITK Image pred_itk_resampled: 
    """
    if transpose:
        pred = pred.T

    # read reference scan and resample reference to spacing of training data
    reference_scan = sitk.ReadImage(reference_scan_path, sitk.sitkFloat32)

    pred_itk = sitk.GetImageFromArray(pred)
    pred_itk.CopyInformation(reference_scan)

    return pred_itk

def predict(input_dir, output_dir, task="Task103_AllStructures", trainer="nnUNetTrainerV2",
            network="3d_fullres", checkpoint="model_final_checkpoint", folds="0,1,2,3,4", 
            store_probability_maps=True, disable_augmentation=False, 
            disable_patch_overlap=False):
    """
    Use trained nnUNet network to generate segmentation masks
    """
    cmd = [
        'nnUNet_predict',
        '-t', task,
        '-i', str(input_dir),
        '-o', str(output_dir),
        '-m', network,
        '-tr', trainer,
        '--num_threads_preprocessing', '2',
        '--num_threads_nifti_save', '1'
    ]

    if folds:
        cmd.append('-f')
        cmd.extend(folds.split(','))

    if checkpoint:
        cmd.append('-chk')
        cmd.append(checkpoint)

    if store_probability_maps:
        cmd.append('--save_npz')

    if disable_augmentation:
        cmd.append('--disable_tta')

    if disable_patch_overlap:
        cmd.extend(['--step_size', '1'])

    cmd_str = " ".join(cmd)
    subprocess.check_call(cmd_str, shell=True)

def process(input_dir, output_dir):
    output_raw_heatmap = False

    # Create temporary directories
    nnunet_input_dir_lowres = tempfile.TemporaryDirectory(dir=output_dir)
    nnunet_output_dir_lowres = tempfile.TemporaryDirectory(dir=output_dir)
    nnunet_input_dir_fullres = tempfile.TemporaryDirectory(dir=output_dir)
    nnunet_output_dir_fullres = tempfile.TemporaryDirectory(dir=output_dir)

    heatmap = Path(output_dir) / "heatmap.mha"
    heatmap_raw = Path(output_dir) / "heatmap_raw.mha"
    segmentation = Path(output_dir) / "segmentation.mha"

    ct_image = Path(input_dir) / "infile_0000.nii.gz"
    itk_img = sitk.ReadImage(str(ct_image), sitk.sitkFloat32)
    image_np = sitk.GetArrayFromImage(itk_img)

    # Get low resolution pancreas segmentation 
    # Downsample image to 256x256
    original_spacing = itk_img.GetSpacing()
    original_size = itk_img.GetSize()
    initial_spacing = np.array(original_spacing)
    print('original_size: ', original_size)
    if original_size[0] > 256:
        scale = original_size[0] / 256
        output_spacing = scale * initial_spacing
        resampled_image = resample_img(itk_img, output_spacing)

    print('resampled_image_size: ', resampled_image.GetSize())

    # Save resampled image
    sitk.WriteImage(resampled_image, str(Path(nnunet_input_dir_lowres.name) / "scan_0000.nii.gz"))

    # Predict pancreas mask using nnUnet
    predict(
        input_dir=nnunet_input_dir_lowres.name,
        output_dir=nnunet_output_dir_lowres.name,
        task="Task105_PancreasDownsampledres256",
        trainer="nnUNetTrainerV2"
    )
    mask_pred_path = str(Path(nnunet_output_dir_lowres.name) / "scan.nii.gz")
    mask_low_res = sitk.ReadImage(mask_pred_path)

    cropped_image, coordinates = GetROIfromDownsampledSegmentation(itk_img, resampled_image, mask_low_res, 80, 50, 10)
    # Save cropped image
    sitk.WriteImage(cropped_image, str(Path(nnunet_input_dir_fullres.name) / "scan_0000.nii.gz"))

    # Predict using nnUNet ensemble, averaging multiple restarts
    # Also need to store the nii.gz predictions for the post-processing
    predict(
        input_dir=nnunet_input_dir_fullres.name,
        output_dir=nnunet_output_dir_fullres.name,
        task="Task103_AllStructures",
        trainer="nnUNetTrainerV2_Loss_CE_checkpoints"
    )
    pred_path_np = str(Path(nnunet_output_dir_fullres.name) / "scan.npz")
    pred_path_nii = str(Path(nnunet_output_dir_fullres.name) / "scan.nii.gz")

    pred_1 = np.load(pred_path_np)['softmax'][1].astype(np.float32)
    pred_1_nii = sitk.ReadImage(pred_path_nii)
    predict(
        input_dir=nnunet_input_dir_fullres.name,
        output_dir=nnunet_output_dir_fullres.name,
        task="Task103_AllStructures",
        trainer="nnUNetTrainerV2_Loss_CE_checkpoints2"
    )
    pred_2 = np.load(pred_path_np)['softmax'][1].astype(np.float32)
    pred_2_nii = sitk.ReadImage(pred_path_nii)
    pred_2_np = sitk.GetArrayFromImage(pred_2_nii).astype(np.uint8)

    # Remove tumour and tumour thrombosis segmentation and reorder
    pred_2_np[pred_2_np == 1] = 0
    pred_2_np[pred_2_np == 8] = 0
    pred_2_np[pred_2_np == 2] = 1
    pred_2_np[pred_2_np == 3] = 2
    pred_2_np[pred_2_np == 4] = 3
    pred_2_np[pred_2_np == 5] = 4
    pred_2_np[pred_2_np == 6] = 5
    pred_2_np[pred_2_np == 7] = 6
    pred_2_np[pred_2_np == 9] = 7

    pred_ensemble = (pred_1 + pred_2) / 2

    softmax_tumor_masked = FPreductionPancreasMaskEnsamble(pred_1_nii, pred_2_nii, pred_ensemble, True)

    pm_image = np.zeros(image_np.shape, dtype=np.float32)
    segmentation_np = np.zeros(image_np.shape, dtype=np.uint8)

    pm_image[coordinates['z_start']:coordinates['z_finish'],
             coordinates['y_start']:coordinates['y_finish'],
             coordinates['x_start']:coordinates['x_finish']] = softmax_tumor_masked

    segmentation_np[coordinates['z_start']:coordinates['z_finish'],
                    coordinates['y_start']:coordinates['y_finish'],
                    coordinates['x_start']:coordinates['x_finish']] = pred_2_np

    segmentation_image = sitk.GetImageFromArray(segmentation_np)
    segmentation_image.CopyInformation(itk_img)

    # Convert nnUNet prediction back to physical space of input scan
    pred_itk_resampled = translate_pred_to_reference_scan_from_file(
        pred=pm_image,
        reference_scan_path=str(ct_image)
    )

    # Save prediction to output folder
    sitk.WriteImage(pred_itk_resampled, str(heatmap), True)
    sitk.WriteImage(segmentation_image, str(segmentation), True)
    subprocess.check_call(["ls", str(Path(output_dir)), "-al"])

    # If output raw heatmap option is enabled, output the unmasked tumor likelihood map...
    if output_raw_heatmap:
        # Zero pad the raw heatmap to match the input image dimensions
        pm_raw_image = np.zeros(image_np.shape, dtype=np.float32)
        pm_raw_image[
            coordinates['z_start']:coordinates['z_finish'],
            coordinates['y_start']:coordinates['y_finish'],
            coordinates['x_start']:coordinates['x_finish']
        ] = pred_ensemble  # softmax_tumor (not masked)
        # Convert nnUNet prediction back to physical space of input scan
        pred_raw_itk_resampled = translate_pred_to_reference_scan_from_file(
            pred=pm_raw_image,
            reference_scan_path=str(ct_image)
        )
        # Save prediction to output folder
        sitk.WriteImage(pred_raw_itk_resampled, str(heatmap_raw), True)

    # Clean up temporary directories
    nnunet_input_dir_lowres.cleanup()
    nnunet_output_dir_lowres.cleanup()
    nnunet_input_dir_fullres.cleanup()
    nnunet_output_dir_fullres.cleanup()
