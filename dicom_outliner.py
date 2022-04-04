"""
Copyright (C) 2022 Abraham George Smith
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import os
import pydicom
import numpy as np
from PyQt5 import QtCore
from skimage.morphology import binary_erosion
from dicom_mask.convert import np_struct_from_patient
from progress_widget import BaseProgressWidget

class Thread(QtCore.QThread):
    progress_change = QtCore.pyqtSignal(int, int, str)
    done = QtCore.pyqtSignal()

    def __init__(self, in_dicom_dir, struct_name, patient, output_dicom_dir):
        super().__init__()
        self.in_dicom_dir = in_dicom_dir
        self.struct_name = struct_name
        self.patient = patient
        self.output_dicom_dir = output_dicom_dir

    def run(self):
        # new ids are created to help solve import problems
        series_instance_uid = pydicom.uid.generate_uid() 
        study_instance_uid = pydicom.uid.generate_uid() 
        frame_of_reference_uid = pydicom.uid.generate_uid() 
        struct_np_image_outline = None 
        self.progress_change.emit(0, 1, 'Extracting structure mask')
        struct_np_image = np_struct_from_patient(self.patient, self.struct_name, case_sensitive=True)
        struct_np_image_outline = np.zeros(struct_np_image.shape) 

        # 2d outline means subtraction is made on every slice on a 2d basis
        for i in range(struct_np_image.shape[0]):
            self.progress_change.emit(i+1, struct_np_image.shape[0], 'Computing outline')
            struct_np_image_outline[i] = struct_np_image[i] - binary_erosion(struct_np_image[i]).astype(int)

        ct_dicom_files = [f for f in os.listdir(self.in_dicom_dir) if 'CT.' in f]
        im_numbers = [int(f.split(' ')[1].replace('.dcm', '')) for f in ct_dicom_files]
        dicom_slices = [x for _, x in sorted(zip(im_numbers, ct_dicom_files))]

        for i, dicom_fname in enumerate(dicom_slices):
            dicom_slice = pydicom.dcmread(os.path.join(self.in_dicom_dir, dicom_fname))
            dicom_slice.SeriesInstanceUID = series_instance_uid
            dicom_slice.StudyInstanceUID = study_instance_uid
            # each slice has it's own SOPInstanceUID
            dicom_slice.SOPInstanceUID = pydicom.uid.generate_uid() 
            dicom_slice.FrameOfReferenceUID = frame_of_reference_uid
            dicom_slice.SeriesDescription = self.struct_name
            dicom_slice.StudyID = self.struct_name
            struct_slice = struct_np_image_outline[i]
            np_pixel_array = dicom_slice.pixel_array
            np_pixel_array[struct_slice > 0] = 3000 # upper end of bone HU value 
            dicom_slice.PixelData = np_pixel_array.tobytes()
            out_path = os.path.join(self.output_dicom_dir, dicom_fname)
            dicom_slice.save_as(out_path)
            self.progress_change.emit(i+1, len(dicom_slices), 'Saving dicom slices')
        self.done.emit()

class ExtractProgressWidget(BaseProgressWidget):

    def __init__(self, feature):
        super().__init__(f'Exporting outlined {feature}')

    def run(self, in_dicom_dir, struct_name, patient, output_dicom_dir):
        self.in_dicom_dir = in_dicom_dir
        self.struct_name = struct_name
        self.patient = patient
        self.output_dicom_dir = output_dicom_dir
        self.progress_bar.setMaximum(len([c for c in os.listdir(in_dicom_dir) if 'CT.' in c]))
        self.thread = Thread(in_dicom_dir, struct_name, patient, output_dicom_dir)
        self.thread.progress_change.connect(self.onCountChanged)
        self.thread.done.connect(self.done)
        self.thread.start()


