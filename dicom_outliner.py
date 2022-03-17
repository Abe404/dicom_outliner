import os
import pydicom
import numpy as np
from skimage.morphology import binary_erosion
from dicom_mask.convert import np_struct_from_patient

def get_mask(patient, struct_name):
    mask = np_struct_from_patient(patient, struct_name, case_sensitive=True)
    return  mask

def add_outline_to_dicom(in_dicom_dir, struct_name, patient, dicom_output_dir):
    uid = pydicom.uid.generate_uid() # a new id is created to help solve import problems

    struct_np_image_outline = None 
    struct_np_image = get_mask(patient, struct_name)
    struct_np_image_outline = np.zeros(struct_np_image.shape) 
    # 2d outline means subtraction is made on every slice on a 2d basis
    for i in range(struct_np_image.shape[0]):
        struct_np_image_outline[i] = struct_np_image[i] - binary_erosion(struct_np_image[i]).astype(int)

    ct_dicom_files = [f for f in os.listdir(in_dicom_dir) if 'CT.' in f]
    im_numbers = [int(f.split(' ')[1].replace('.dcm', '')) for f in ct_dicom_files]
    dicom_slices = [x for _, x in sorted(zip(im_numbers, ct_dicom_files))]

    for i, dicom_fname in enumerate(dicom_slices):
        dicom_slice = pydicom.dcmread(os.path.join(in_dicom_dir, dicom_fname))
        dicom_slice.SeriesInstanceUID = uid
        dicom_slice.SeriesDescription = struct_name
        struct_slice = struct_np_image_outline[i]
        np_pixel_array = dicom_slice.pixel_array
        np_pixel_array[struct_slice > 0] = 3000 # upper end of bone HU value 
        dicom_slice.PixelData = np_pixel_array.tobytes()
        out_path = os.path.join(dicom_output_dir, dicom_fname)

        dicom_slice.save_as(out_path)


def export_outline(in_dicom_dir, struct_name, patient, output_dicom_dir):
    add_outline_to_dicom(in_dicom_dir, struct_name, patient, output_dicom_dir)