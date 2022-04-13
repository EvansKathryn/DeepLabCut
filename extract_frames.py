import os
import sys
import logging

from PySide2.QtWidgets import QWidget, QComboBox, QSpinBox, QButtonGroup
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon

from deeplabcut.utils import auxiliaryfunctions
from deeplabcut.generate_training_dataset import extract_frames

from components import _create_horizontal_layout


class ExtractFrames(QWidget):
    def __init__(self, parent, cfg):
        super(ExtractFrames, self).__init__(parent)

        self.logger = logging.getLogger("GUI")
        
        # variable initilization
        self.method = "automatic"
        self.crop = False
        self.feedback = False
        self.opencv = True

        self.config = cfg

        self.separatorLine = QtWidgets.QFrame()
        self.separatorLine.setFrameShape(QtWidgets.QFrame.HLine)
        self.separatorLine.setFrameShadow(QtWidgets.QFrame.Raised)

        self.separatorLine.setLineWidth(0)
        self.separatorLine.setMidLineWidth(1)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignTop)
        self.main_layout.setSpacing(20)
        self.main_layout.setContentsMargins(0, 20, 10, 20)
        self.setLayout(self.main_layout)

        l1_step1 = QtWidgets.QLabel("DeepLabCut - Step 2. Extract Frames")
        l1_step1.setStyleSheet("font:bold")    
        l1_step1.setContentsMargins(20, 0, 0, 10)

        self.main_layout.addWidget(l1_step1)
        self.main_layout.addWidget(self.separatorLine)

        layout_config = _create_horizontal_layout()
        self._generate_config_layout(layout_config)
        self.main_layout.addLayout(layout_config)

        self.layout_attributes = QtWidgets.QVBoxLayout()
        self.layout_attributes.setAlignment(Qt.AlignTop)
        self.layout_attributes.setSpacing(20)
        self.layout_attributes.setContentsMargins(0, 0, 40, 50)

        label = QtWidgets.QLabel("Attributes")
        label.setStyleSheet("font:bold")
        label.setContentsMargins(20, 20, 0, 10)
        self.layout_attributes.addWidget(label)

        self.layout_opt = QtWidgets.QHBoxLayout()
        self.layout_opt.setAlignment(Qt.AlignLeft)
        self.layout_opt.setSpacing(60)
        self.layout_opt.setContentsMargins(20, 0, 50, 0)

        self._choose()
        self._crop()
        self._feedback()
        self._openCV()

        self.layout_select_specify = QtWidgets.QHBoxLayout()
        self.layout_select_specify.setAlignment(Qt.AlignLeft)
        self.layout_select_specify.setSpacing(60)
        self.layout_select_specify.setContentsMargins(20, 20, 50, 0)

        self._select_alg()
        self._specify_step()
        self._specify_width()

        self.ok_button = QtWidgets.QPushButton("Ok")
        # self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self.extract_frames)

        self.layout_attributes.addLayout(self.layout_opt)
        self.layout_attributes.addLayout(self.layout_select_specify)
        self.layout_attributes.addWidget(self.ok_button, alignment=Qt.AlignRight)

        self.main_layout.addLayout(self.layout_attributes)

    def _generate_config_layout(self, layout):
        cfg_text = QtWidgets.QLabel("Active config file:")

        self.cfg_line = QtWidgets.QLineEdit()
        self.cfg_line.setMinimumHeight(30)
        self.cfg_line.setText(self.config)
        self.cfg_line.textChanged[str].connect(self.update_cfg)

        browse_button = QtWidgets.QPushButton("Browse")
        browse_button.setMaximumWidth(100)
        browse_button.setMinimumHeight(30)
        browse_button.clicked.connect(self.browse_dir)

        layout.addWidget(cfg_text)
        layout.addWidget(self.cfg_line)
        layout.addWidget(browse_button)

    def _choose(self):
        l_opt1 = QtWidgets.QVBoxLayout()
        l_opt1.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        l_opt1.setSpacing(20)
        l_opt1.setContentsMargins(20, 0, 0, 0)

        self.btngroup1 = QButtonGroup()

        opt1_text = QtWidgets.QLabel("Choose the extraction method")
        self.method_choice_rb1 = QtWidgets.QRadioButton("automatic")
        self.method_choice_rb1.setChecked(True)
        self.method_choice_rb1.toggled.connect(
            lambda: self.select_extract_method(self.method_choice_rb1)
        )

        self.method_choice_rb2 = QtWidgets.QRadioButton("manual")
        self.method_choice_rb2.clicked.connect(
            lambda: self.select_extract_method(self.method_choice_rb2)
        )

        self.btngroup1.addButton(self.method_choice_rb1)
        self.btngroup1.addButton(self.method_choice_rb2)
        l_opt1.addWidget(opt1_text)
        l_opt1.addWidget(self.method_choice_rb1)
        l_opt1.addWidget(self.method_choice_rb2)

        self.layout_opt.addLayout(l_opt1)

    def _crop(self):
        l_opt = QtWidgets.QVBoxLayout()
        l_opt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        l_opt.setSpacing(20)
        l_opt.setContentsMargins(20, 0, 0, 0)

        opt_text = QtWidgets.QLabel("Want to crop the frames?")
        self.btngroup_crop = QButtonGroup()

        self.crop_choice1 = QtWidgets.QRadioButton("False")
        self.crop_choice1.setChecked(True)
        self.crop_choice1.toggled.connect(
            lambda: self.update_crop_choice(self.crop_choice1)
        )

        self.crop_choice2 = QtWidgets.QRadioButton("True (read from config file)")
        self.crop_choice2.toggled.connect(
            lambda: self.update_crop_choice(self.crop_choice2)
        )

        self.crop_choice3 = QtWidgets.QRadioButton("GUI")
        self.crop_choice3.toggled.connect(
            lambda: self.update_crop_choice(self.crop_choice3)
        )

        self.btngroup_crop.addButton(self.crop_choice1)
        self.btngroup_crop.addButton(self.crop_choice2)
        self.btngroup_crop.addButton(self.crop_choice3)

        l_opt.addWidget(opt_text)
        l_opt.addWidget(self.crop_choice1)
        l_opt.addWidget(self.crop_choice2)
        l_opt.addWidget(self.crop_choice3)

        self.layout_opt.addLayout(l_opt)

    def _feedback(self):
        l_opt = QtWidgets.QVBoxLayout()
        l_opt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        l_opt.setSpacing(20)
        l_opt.setContentsMargins(20, 0, 0, 0)

        self.set_user_feedback = QtWidgets.QCheckBox("User feedback")
        self.set_user_feedback.setCheckState(Qt.Checked)
        self.set_user_feedback.stateChanged.connect(self.update_feedback_choice)

        l_opt.addWidget(self.set_user_feedback)
        self.layout_opt.addLayout(l_opt)

    def _openCV(self):
        l_opt = QtWidgets.QVBoxLayout()
        l_opt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        l_opt.setSpacing(20)
        l_opt.setContentsMargins(20, 0, 0, 0)

        self.use_openCV_checkbox = QtWidgets.QCheckBox("Use openCV")
        self.use_openCV_checkbox.setCheckState(Qt.Checked)
        self.use_openCV_checkbox.stateChanged.connect(self.update_opencv_choice)
        self.use_openCV_checkbox.setToolTip(
            "Recommended. Uses openCV for managing videos instead of moviepy (legacy)."
        )

        l_opt.addWidget(self.use_openCV_checkbox)

        self.layout_opt.addLayout(l_opt)

    def _select_alg(self):
        l_opt = QtWidgets.QVBoxLayout()
        l_opt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        l_opt.setSpacing(20)
        l_opt.setContentsMargins(20, 0, 0, 0)

        opt_text = QtWidgets.QLabel("Select the algorithm")
        self.algo_choice = QComboBox()
        self.algo_choice.setMinimumWidth(300)
        self.algo_choice.setMinimumHeight(30)
        self.algo_choice.addItem("kmeans")
        self.algo_choice.addItem("uniform")

        l_opt.addWidget(opt_text)
        l_opt.addWidget(self.algo_choice)
        self.layout_select_specify.addLayout(l_opt)

    def _specify_step(self):
        l_opt = QtWidgets.QVBoxLayout()
        l_opt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        l_opt.setSpacing(20)
        l_opt.setContentsMargins(20, 0, 0, 0)

        opt_text = QtWidgets.QLabel("Specify the cluster step")
        self.cluster_step_spin = QSpinBox()
        self.cluster_step_spin.setValue(1)
        self.cluster_step_spin.setMinimumWidth(300)
        self.cluster_step_spin.setMinimumHeight(30)

        l_opt.addWidget(opt_text)
        l_opt.addWidget(self.cluster_step_spin)
        self.layout_select_specify.addLayout(l_opt)

    def _specify_width(self):
        l_opt = QtWidgets.QVBoxLayout()
        l_opt.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        l_opt.setSpacing(20)
        l_opt.setContentsMargins(20, 0, 0, 0)

        opt_text = QtWidgets.QLabel("Specify the GUI slider width")
        self.slider_width = QSpinBox()
        self.slider_width.setValue(25)
        self.slider_width.setMinimumWidth(300)
        self.slider_width.setMinimumHeight(30)

        l_opt.addWidget(opt_text)
        l_opt.addWidget(self.slider_width)
        self.layout_select_specify.addLayout(l_opt)

    def update_cfg(self):
        text = self.cfg_line.text()
        self.config = text
        self.cfg = auxiliaryfunctions.read_config(self.config)

    def browse_dir(self):
        cwd = self.config
        config = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select a configuration file", cwd, "Config files (*.yaml)"
        )
        if not config[0]:
            return
        self.config = config[0]
        self.cfg_line.setText(self.config)

    def select_extract_method(self, rb_method):
        self.method = rb_method.text()
        print(self.method)
        if self.method == "manual":
            self.crop_choice1.setEnabled(False)
            self.crop_choice2.setEnabled(False)
            self.crop_choice3.setEnabled(False)

            self.feedback_choice1.setEnabled(False)
            self.feedback_choice2.setEnabled(False)

            self.opencv_choice1.setEnabled(False)
            self.opencv_choice2.setEnabled(False)

            self.algo_choice.setEnabled(False)
            self.cluster_step_spin.setEnabled(False)
            self.slider_width.setEnabled(False)
        else:
            self.crop_choice1.setEnabled(True)
            self.crop_choice2.setEnabled(True)
            self.crop_choice3.setEnabled(True)

            self.feedback_choice1.setEnabled(True)
            self.feedback_choice2.setEnabled(True)

            self.opencv_choice1.setEnabled(True)
            self.opencv_choice2.setEnabled(True)

            self.algo_choice.setEnabled(True)
            self.cluster_step_spin.setEnabled(True)
            self.slider_width.setEnabled(True)

    def update_crop_choice(self, rb):
        if rb.text() == "True (read from config file)":
            self.crop = True
        elif rb.text() == "GUI":
            self.crop = "GUI"
        else:
            self.crop = False

    def update_feedback_choice(self, s):
        if s == Qt.Checked:
            self.feedback = True
            self.logger.info("Enabling user feedback.")
        else:
            self.feedback = False
            self.logger.info("Disabling user feedback.")

    def update_opencv_choice(self, s):
        if s == Qt.Checked:
            self.opencv = True
            self.logger.info("Use openCV enabled.")
        else:
            self.opencv = False
            self.logger.info("Use openCV disabled. Using moviepy..")

    def extract_frames(self):
        mode = self.method
        algo = self.algo_choice.currentText()
        crop = self.crop
        userfeedback = self.feedback
        opencv = self.opencv
        clusterstep = self.cluster_step_spin.value()
        slider_width = self.slider_width.value()

        extract_frames(
            self.config,
            mode,
            algo,
            crop=crop,
            userfeedback=userfeedback,
            cluster_step=clusterstep,
            cluster_resizewidth=30,
            cluster_color=False,
            opencv=opencv,
            slider_width=slider_width,
        )

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Frames were successfully extracted, for the videos of interest.")

        msg.setWindowTitle("Info")
        msg.setMinimumWidth(900)
        self.logo_dir = os.path.dirname(os.path.realpath("logo.png")) + os.path.sep
        self.logo = self.logo_dir + "/assets/logo.png"
        msg.setWindowIcon(QIcon(self.logo))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
