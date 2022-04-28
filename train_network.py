import os

from PySide2.QtWidgets import QWidget, QSpinBox, QButtonGroup
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon

import deeplabcut
from deeplabcut.utils import auxiliaryfunctions

from components import DefaultTab, EditYamlButton, ShuffleSpinBox, TrainingSetSpinBox, _create_grid_layout, _create_horizontal_layout, _create_label_widget
from widgets import ConfigEditor


class TrainNetwork(DefaultTab):
   
    def __init__(self, root, parent, h1_description):
        super(TrainNetwork, self).__init__(root, parent, h1_description)

        pose_cfg = auxiliaryfunctions.read_plainconfig(self.root.pose_cfg_path)
        self.display_iters = str(pose_cfg["display_iters"])
        self.save_iters = str(pose_cfg["save_iters"])
        self.MAX_ITERS = 10000000

        self.set_page()

    def set_page(self):

        self.main_layout.addWidget(
            _create_label_widget("Attributes", "font:bold")
        )
        self.layout_attributes = _create_grid_layout(margins=(20, 0, 0, 0))
        self._generate_layout_attributes(self.layout_attributes)
        self.main_layout.addLayout(self.layout_attributes)


        self.main_layout.addWidget(_create_label_widget("")) #dummy label

        self.edit_posecfg_btn = QtWidgets.QPushButton("Edit pose_cfg.yaml")
        self.edit_posecfg_btn.setMinimumWidth(150)
        self.edit_posecfg_btn.clicked.connect(self.open_posecfg_editor)

        self.ok_button = QtWidgets.QPushButton("Train Network")
        self.ok_button.setMinimumWidth(150)
        self.ok_button.clicked.connect(self.train_network)
        
        self.main_layout.addWidget(self.edit_posecfg_btn, alignment=Qt.AlignRight)
        self.main_layout.addWidget(self.ok_button, alignment=Qt.AlignRight)


    def _generate_layout_attributes(self, layout):
        # Shuffle
        shuffle_label = QtWidgets.QLabel("Shuffle")
        self.shuffle = ShuffleSpinBox(root=self.root, parent=self)
        self.shuffle.setMinimumWidth(150)

        # Trainingset index
        trainingset_label = QtWidgets.QLabel("Trainingset index")
        self.trainingset = TrainingSetSpinBox(root=self.root, parent=self)
        self.trainingset.setMinimumWidth(150)

        # Display iterations
        dispiters_label = QtWidgets.QLabel("Display iterations")
        self.display_iters_spin = QSpinBox()
        self.display_iters_spin.setMinimumWidth(150)
        self.display_iters_spin.setMinimum(1)
        self.display_iters_spin.setMaximum(int(self.MAX_ITERS))
        self.display_iters_spin.setValue(1000)
        self.display_iters_spin.valueChanged.connect(self.log_display_iters)

        # Save iterations
        saveiters_label = QtWidgets.QLabel("Save iterations")
        self.save_iters_spin = QSpinBox()
        self.save_iters_spin.setMinimumWidth(150)
        self.save_iters_spin.setMinimum(1)
        self.save_iters_spin.setMaximum(int(self.MAX_ITERS))
        self.save_iters_spin.setValue(50000)
        self.save_iters_spin.valueChanged.connect(self.log_save_iters)

        # Max iterations
        maxiters_label = QtWidgets.QLabel("Maximum iterations")
        self.max_iters_spin = QSpinBox()
        self.max_iters_spin.setMinimumWidth(150)
        self.max_iters_spin.setMinimum(1)
        self.max_iters_spin.setMaximum(int(self.MAX_ITERS))
        self.max_iters_spin.setValue(100000)
        self.max_iters_spin.valueChanged.connect(self.log_max_iters)

        # Max number snapshots to keep
        snapkeep_label = QtWidgets.QLabel("Number of snapshots to keep")
        self.snapshots = QSpinBox()
        self.snapshots.setMinimumWidth(150)
        self.snapshots.setValue(5)
        self.snapshots.setMinimum(1)
        self.snapshots.setMaximum(100)
        self.snapshots.valueChanged.connect(self.log_snapshots)

        layout.addWidget(shuffle_label, 0, 0)
        layout.addWidget(self.shuffle, 0, 1)
        layout.addWidget(trainingset_label, 0, 2)
        layout.addWidget(self.trainingset, 0, 3)
        layout.addWidget(dispiters_label, 1, 0)
        layout.addWidget(self.display_iters_spin, 1, 1)
        layout.addWidget(saveiters_label, 1, 2)
        layout.addWidget(self.save_iters_spin, 1, 3)
        layout.addWidget(maxiters_label, 1, 4)
        layout.addWidget(self.max_iters_spin, 1, 5)
        layout.addWidget(snapkeep_label, 1, 6)
        layout.addWidget(self.snapshots, 1, 7)
        # layout.addWidget()

    def log_display_iters(self, value):
        self.root.logger.info(f"Display iters set to {value}")

    def log_save_iters(self, value):
        self.root.logger.info(f"Save iters set to {value}")

    def log_max_iters(self, value):
        self.root.logger.info(f"Max iters set to {value}")

    def log_snapshots(self, value):
        self.root.logger.info(f"Max snapshots to keep set to {value}")

    def open_posecfg_editor(self):
        editor = ConfigEditor(self.root.pose_cfg_path)
        editor.show()

    def train_network(self):

        config = self.root.config
        shuffle = int(self.shuffle.value())
        trainingsetindex = int(self.trainingset.value())
        max_snapshots_to_keep = int(self.snapshots.value())
        displayiters = int(self.display_iters_spin.value())
        saveiters = int(self.save_iters_spin.value())
        maxiters = int(self.max_iters_spin.value())

        deeplabcut.train_network(
            config,
            shuffle,
            trainingsetindex,
            gputouse=None,
            max_snapshots_to_keep=max_snapshots_to_keep,
            autotune=None,
            displayiters=displayiters,
            saveiters=saveiters,
            maxiters=maxiters,
        )
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("The network is now trained and ready to evaluate.")
        msg.setInformativeText(
            "Use the function 'evaluate_network' to evaluate the network."
        )

        msg.setWindowTitle("Info")
        msg.setMinimumWidth(900)
        self.logo_dir = os.path.dirname(os.path.realpath("logo.png")) + os.path.sep
        self.logo = self.logo_dir + "/assets/logo.png"
        msg.setWindowIcon(QIcon(self.logo))
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg.exec_()
