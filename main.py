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

import sys
import os
from PyQt5 import QtWidgets  
from PyQt5 import QtCore
from PyQt5 import QtGui
import glob
from dicom_mask.convert import load_patient
from dicom_outliner import ExtractProgressWidget


class MainWindow(QtWidgets.QMainWindow):

    def add_info_label(self):
        self.info_label = QtWidgets.QLabel()
        self.info_label.setText('')
        self.layout.addWidget(self.info_label)


    def export_dicom(self):
        print('export files now. struct name = ', self.struct_name, 'source_dicom_dir = ',
              self.source_dicom_dir, 'output directory = ', self.output_dicom_dir)
        self.progress_widget = ExtractProgressWidget(self.struct_name)
        self.progress_widget.show()
        self.progress_widget.run(self.source_dicom_dir, self.struct_name, self.patient, self.output_dicom_dir)
        self.info_label.setText('Outline dicom exported to ' + self.output_dicom_dir)

    def add_export_button(self):
        self.export_button = QtWidgets.QPushButton('export')
        self.export_button.clicked.connect(self.export_dicom)
        self.export_button.hide()
        self.layout.addWidget(self.export_button)

    def add_series_name_label(self):
        self.series_name_label = QtWidgets.QLabel()
        self.series_name_label.setText('Series name')
        self.series_name_label.hide()
        self.layout.addWidget(self.series_name_label)


    def add_select_input_directory_button(self):
        # Add specify image directory button
        directory_label = QtWidgets.QLabel()
        directory_label.setText("Source dicom directory: Not yet specified")
        self.layout.addWidget(directory_label)
        self.directory_label = directory_label

        specify_input_dicom_dir_btn = QtWidgets.QPushButton('Specify source dicom directory')
        specify_input_dicom_dir_btn.clicked.connect(self.select_input_dicom_dir)
        self.layout.addWidget(specify_input_dicom_dir_btn)


    def add_select_output_directory_button(self):
        # Add specify image directory button
        output_directory_label = QtWidgets.QLabel()
        output_directory_label.setText("Output dicom directory: Not yet specified")
        self.layout.addWidget(output_directory_label)
        self.output_directory_label = output_directory_label

        self.specify_output_dicom_dir_btn = QtWidgets.QPushButton('Specify output dicom directory')
        self.specify_output_dicom_dir_btn.clicked.connect(self.select_output_dicom_dir)
        self.layout.addWidget(self.specify_output_dicom_dir_btn)
        self.output_directory_label.hide()
        self.specify_output_dicom_dir_btn.hide()

    def select_input_dicom_dir(self):
        self.image_dialog = QtWidgets.QFileDialog(self)
        self.image_dialog.setFileMode(QtWidgets.QFileDialog.Directory)

        def input_dir_selected():
            self.source_dicom_dir = self.image_dialog.selectedFiles()[0]
            self.directory_label.setText('Input dicom directory: ' + self.source_dicom_dir)
            dicom_file_names = os.listdir(self.source_dicom_dir)
            self.patient = load_patient(self.source_dicom_dir, dicom_file_names)
            self.output_directory_label.show()
            self.specify_output_dicom_dir_btn.show()
            self.info_label.setText("Dicom struct and output directory must be specified")
            self.show_struct_combo()

        self.image_dialog.fileSelected.connect(input_dir_selected)
        self.image_dialog.open()


    def select_output_dicom_dir(self):
        self.image_dialog = QtWidgets.QFileDialog(self)
        self.image_dialog.setFileMode(QtWidgets.QFileDialog.Directory)

        def output_dir_selected():
            self.output_dicom_dir = self.image_dialog.selectedFiles()[0]
            self.output_directory_label.setText('Output dicom directory: ' + self.output_dicom_dir)
            self.export_button.show()
            self.info_label.setText('')

        self.image_dialog.fileSelected.connect(output_dir_selected)
        self.image_dialog.open()

    def show_struct_combo(self):
        self.struct_combo_label.show()
        self.struct_combo.show()
        self.struct_combo.clear()
        self.struct_combo.addItems([s['name'] for s in self.patient['structures'].values()])

    def add_struct_combo(self):
        # select which struct will be output.
        self.struct_combo_label = QtWidgets.QLabel()
        self.struct_combo_label.setText("Struct to use for outline:")
        self.layout.addWidget(self.struct_combo_label)
        self.struct_combo_label.hide()
 
        self.struct_combo = QtWidgets.QComboBox()
        self.struct_combo.currentIndexChanged.connect(self.struct_combo_selection_change)
        self.layout.addWidget(self.struct_combo)
        self.struct_combo.hide()

    def struct_combo_selection_change(self, _):
        self.struct_name = self.struct_combo.currentText()
        self.series_name_label.show()
        self.series_name_label.setText('Series name: ' + self.struct_name)

    def create_ui(self):
        self.setWindowTitle("dicom outliner")
        container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout()
        container.setLayout(container_layout)
        self.layout = container_layout
        self.setCentralWidget(container)
        self.add_select_input_directory_button()
        self.add_struct_combo()
        self.add_series_name_label()
        self.add_select_output_directory_button()
        self.add_info_label()
        self.add_export_button()

    def __init__(self):
        super().__init__()
        self.create_ui()
        self.info_label.setText("Dicom series input folder must be specified")


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())