from PySide2 import QtWidgets
from PySide2.QtCore import Qt

from dlc_params import DLC_Params
from components import (
    DefaultTab,
    _create_grid_layout,
    _create_label_widget,
)

from deeplabcut.generate_training_dataset import extract_frames


class ExtractFrames(DefaultTab):
    def __init__(self, root, parent, h1_description):
        super(ExtractFrames, self).__init__(root, parent, h1_description)

        self.set_page()

    def set_page(self):

        self.main_layout.addWidget(_create_label_widget("Attributes", "font:bold"))
        self.layout_attributes = _create_grid_layout(margins=(20, 0, 0, 0))
        self._generate_layout_attributes(self.layout_attributes)
        self.main_layout.addLayout(self.layout_attributes)

        self.ok_button = QtWidgets.QPushButton("Extract frames")
        self.ok_button.clicked.connect(self.extract_frames)
        self.main_layout.addWidget(self.ok_button, alignment=Qt.AlignRight)

    def _generate_layout_attributes(self, layout):

        # Extraction method
        ext_method_label = QtWidgets.QLabel("Extraction method")
        self.extraction_method_widget = QtWidgets.QComboBox()
        options = ["automatic", "manual"]
        self.extraction_method_widget.addItems(options)
        self.extraction_method_widget.currentTextChanged.connect(
            self.log_extraction_method
        )

        # User feedback
        self.user_feedback_checkbox = QtWidgets.QCheckBox("User feedback")
        self.user_feedback_checkbox.setCheckState(Qt.Unchecked)
        self.user_feedback_checkbox.stateChanged.connect(self.log_user_feedback_choice)
        self.user_feedback_checkbox.hide()  # NOTE: Not sure what feedback should be doing

        # Frame extraction algorithm
        ext_algo_label = QtWidgets.QLabel("Extraction algorithm")
        self.extraction_algorithm_widget = QtWidgets.QComboBox()
        self.extraction_algorithm_widget.addItems(
            DLC_Params.FRAME_EXTRACTION_ALGORITHMS
        )
        self.extraction_algorithm_widget.currentTextChanged.connect(
            self.log_extraction_algorithm
        )

        # Frame cropping
        frame_crop_label = QtWidgets.QLabel("Frame cropping")
        self.frame_cropping_widget = QtWidgets.QComboBox()
        self.frame_cropping_widget.addItems(["disabled", "read from config", "GUI"])
        self.frame_cropping_widget.currentTextChanged.connect(
            self.log_frame_cropping_choice
        )

        # Cluster step
        cluster_step_label = QtWidgets.QLabel("Cluster step")
        self.cluster_step_widget = QtWidgets.QSpinBox()
        self.cluster_step_widget.setValue(25)

        # GUI Slider width
        gui_slider_label = QtWidgets.QLabel("GUI slider width")
        self.slider_width_widget = QtWidgets.QSpinBox()
        self.slider_width_widget.setValue(25)
        self.slider_width_widget.setEnabled(False)

        layout.addWidget(self.user_feedback_checkbox, 0, 1)

        layout.addWidget(ext_method_label, 1, 0)
        layout.addWidget(self.extraction_method_widget, 1, 1)
        layout.addWidget(gui_slider_label, 1, 2)
        layout.addWidget(self.slider_width_widget, 1, 3)

        layout.addWidget(ext_algo_label, 2, 0)
        layout.addWidget(self.extraction_algorithm_widget, 2, 1)
        layout.addWidget(cluster_step_label, 2, 2)
        layout.addWidget(self.cluster_step_widget, 2, 3)

        layout.addWidget(frame_crop_label, 3, 0)
        layout.addWidget(self.frame_cropping_widget, 3, 1)

    def log_user_feedback_choice(self, state):
        if state == Qt.Checked:
            self.root.logger.info("User feedback ENABLED")
        else:
            self.root.logger.info("User feedback DISABLED")

    def log_extraction_algorithm(self, extraction_algorithm):
        self.root.logger.info(f"Extraction method set to {extraction_algorithm}")

    def log_extraction_method(self, extraction_method):
        self.root.logger.info(f"Extraction method set to {extraction_method}")
        if extraction_method == "manual":
            self.extraction_algorithm_widget.setEnabled(False)
            self.cluster_step_widget.setEnabled(False)
            self.slider_width_widget.setEnabled(True)
        else:
            self.extraction_algorithm_widget.setEnabled(True)
            self.cluster_step_widget.setEnabled(True)
            self.slider_width_widget.setEnabled(False)

    def log_frame_cropping_choice(self, cropping_option):
        self.root.logger.info(f"Cropping set to '{cropping_option}'")

    def update_feedback_choice(self, s):
        if s == Qt.Checked:
            self.feedback = True
            self.root.logger.info("Enabling user feedback.")
        else:
            self.feedback = False
            self.root.logger.info("Disabling user feedback.")

    def extract_frames(self):
        config = self.root.config
        mode = self.extraction_method_widget.currentText()
        algo = self.extraction_algorithm_widget.currentText()
        userfeedback = self.user_feedback_checkbox.checkState() == Qt.Checked
        clusterstep = self.cluster_step_widget.value()
        slider_width = self.slider_width_widget.value()

        crop = False  # default value
        if self.frame_cropping_widget.currentText() == "GUI":
            # TODO: Plug GUI cropping
            raise NotImplementedError
        elif self.frame_cropping_widget.currentText() == "read from config":
            crop = True

        extract_frames(
            config,
            mode,
            algo,
            crop=crop,
            userfeedback=userfeedback,
            cluster_step=clusterstep,
            cluster_resizewidth=30,
            cluster_color=False,
            slider_width=slider_width,
        )

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Frames were successfully extracted, for the videos of interest.")

        msg.setWindowTitle("Info")
        msg.setWindowIcon(QtWidgets.QMessageBox.Information)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
