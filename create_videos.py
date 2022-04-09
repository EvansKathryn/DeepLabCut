import logging

import deeplabcut
from deeplabcut.utils import auxiliaryfunctions

from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QWidget,
    QComboBox,
    QSpinBox,
)

from components import (
    _create_horizontal_layout,
    _create_label_widget,
    _create_vertical_layout,
    BrowseFilesButton,
)


class CreateVideos(QWidget):
    def __init__(self, parent, cfg):
        super(CreateVideos, self).__init__(parent)

        self.logger = logging.getLogger("GUI")

        self.filelist = set()
        self.config = cfg
        self.cfg = auxiliaryfunctions.read_config(self.config)

        self.all_bodyparts = []

        if self.cfg["multianimalproject"]:
            self.all_bodyparts = self.cfg["multianimalbodyparts"]
        else:
            self.all_bodyparts = self.cfg["bodyparts"]

        self.bodyparts_to_use = self.all_bodyparts

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self.set_page()

    def set_page(self):

        self.main_layout.addWidget(
            _create_label_widget(
                "DeepLabCut - Optional Step. Create Videos",
                "font:bold; font-size:18px;",
                (20, 20, 0, 10),
            )
        )

        layout_config = _create_horizontal_layout()
        self._generate_config_layout(layout_config)
        self.main_layout.addLayout(layout_config)

        self.main_layout.addWidget(_create_label_widget("Video Selection", "font:bold"))
        self.layout_video_selection = _create_horizontal_layout()
        self._generate_layout_video_analysis(self.layout_video_selection)
        self.main_layout.addLayout(self.layout_video_selection)

        self.main_layout.addWidget(
            _create_label_widget("Analysis Attributes", "font:bold")
        )
        self.layout_attributes = _create_horizontal_layout()
        self._generate_layout_attributes(self.layout_attributes)
        self.main_layout.addLayout(self.layout_attributes)

        self.layout_multi_animal = _create_horizontal_layout()

        if self.cfg.get("multianimalproject", False):
            self.main_layout.addWidget(
                _create_label_widget("Multi-animal settings", "font:bold")
            )
            self._generate_layout_multianimal_only_options(self.layout_multi_animal)
            self.main_layout.addLayout(self.layout_multi_animal)

        self.main_layout.addWidget(
            _create_label_widget("Video Parameters", "font:bold")
        )
        self.layout_video_parameters = _create_vertical_layout()
        self._generate_layout_video_parameters(self.layout_video_parameters)
        self.main_layout.addLayout(self.layout_video_parameters)

        self.run_button = QtWidgets.QPushButton("Create videos")
        self.run_button.clicked.connect(self.create_videos)
        self.main_layout.addWidget(self.run_button, alignment=Qt.AlignRight)

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

    def _generate_layout_video_analysis(self, layout):

        self.videotype_widget = QComboBox()
        self.videotype_widget.setMaximumWidth(100)
        self.videotype_widget.setMinimumHeight(30)

        options = ["avi", "mp4", "mov"]
        self.videotype_widget.addItems(options)
        self.videotype_widget.setCurrentText("avi")
        self.videotype_widget.currentTextChanged.connect(self.update_videotype)

        layout.addWidget(self.videotype_widget)

        """
        # NOTE: Reusable file selecting button -- not entirely there yet
        self.select_video_button = BrowseFilesButton(
            "Select videos",
            ".avi",
            single_file=False,
            parent=self
            )
        self.select_video_button.setMaximumWidth(200)
        self.select_video_button.setMinimumHeight(30)
        """
        self.select_video_button = QtWidgets.QPushButton("Select videos")
        self.select_video_button.setMaximumWidth(200)
        self.select_video_button.setMinimumHeight(30)
        self.select_video_button.clicked.connect(self.select_videos)

        layout.addWidget(self.select_video_button)

        self.selected_videos_text = QtWidgets.QLabel("")
        layout.addWidget(self.selected_videos_text)

    def _generate_layout_multianimal_only_options(self, layout):
        tmp_text = QtWidgets.QLabel("Color keypoints by:")
        self.color_by_widget = QComboBox()
        self.color_by_widget.setMaximumWidth(150)
        self.color_by_widget.setMinimumHeight(30)
        self.color_by_widget.addItems(["bodypart", "individual"])
        self.color_by_widget.setCurrentText("bodypart")
        self.color_by_widget.currentTextChanged.connect(self.update_color_by)

        layout.addWidget(tmp_text)
        layout.addWidget(self.color_by_widget)

    def _generate_layout_attributes(self, layout):
        # Shuffle
        opt_text = QtWidgets.QLabel("Shuffle")
        self.shuffle = QSpinBox()
        self.shuffle.setMaximum(100)
        self.shuffle.setValue(1)
        self.shuffle.setMinimumHeight(30)

        layout.addWidget(opt_text)
        layout.addWidget(self.shuffle)

        # Trainingset index
        opt_text = QtWidgets.QLabel("Trainingset index")
        self.trainingset = QSpinBox()
        self.trainingset.setMaximum(100)
        self.trainingset.setValue(0)
        self.trainingset.setMinimumHeight(30)

        layout.addWidget(opt_text)
        layout.addWidget(self.trainingset)

        # Overwrite videos
        self.overwrite_videos = QtWidgets.QCheckBox("Overwrite videos")
        self.overwrite_videos.setCheckState(Qt.Unchecked)
        self.overwrite_videos.stateChanged.connect(self.update_overwrite_videos)

        layout.addWidget(self.overwrite_videos)

    def _generate_layout_video_parameters(self, layout):

        tmp_layout = _create_horizontal_layout()

        # Trail Points
        opt_text = QtWidgets.QLabel("Specify the number of trail points")
        self.trail_points = QSpinBox()
        self.trail_points.setValue(0)
        self.trail_points.setMinimumWidth(100)
        self.trail_points.setMinimumHeight(30)
        tmp_layout.addWidget(opt_text)
        tmp_layout.addWidget(self.trail_points)

        layout.addLayout(tmp_layout)

        tmp_layout = _create_vertical_layout()

        # Plot all bodyparts
        self.plot_all_bodyparts = QtWidgets.QCheckBox("Plot all bodyparts")
        self.plot_all_bodyparts.setCheckState(Qt.Checked)
        self.plot_all_bodyparts.stateChanged.connect(self.update_use_all_bodyparts)
        tmp_layout.addWidget(self.plot_all_bodyparts)

        # Skeleton
        self.draw_skeleton_checkbox = QtWidgets.QCheckBox("Draw skeleton")
        self.draw_skeleton_checkbox.setCheckState(Qt.Checked)
        self.draw_skeleton_checkbox.stateChanged.connect(self.update_draw_skeleton)
        tmp_layout.addWidget(self.draw_skeleton_checkbox)

        # Filtered data
        self.use_filtered_data_checkbox = QtWidgets.QCheckBox("Use filtered data")
        self.use_filtered_data_checkbox.setCheckState(Qt.Unchecked)
        self.use_filtered_data_checkbox.stateChanged.connect(
            self.update_use_filtered_data
        )
        tmp_layout.addWidget(self.use_filtered_data_checkbox)

        # Plot trajectories
        self.plot_trajectories = QtWidgets.QCheckBox("Plot trajectories")
        self.plot_trajectories.setCheckState(Qt.Unchecked)
        self.plot_trajectories.stateChanged.connect(self.update_plot_trajectory_choice)
        tmp_layout.addWidget(self.plot_trajectories)

        # High quality video
        self.create_high_quality_video = QtWidgets.QCheckBox(
            "High quality video (slow)"
        )
        self.create_high_quality_video.setCheckState(Qt.Unchecked)
        self.create_high_quality_video.stateChanged.connect(
            self.update_high_quality_video
        )
        tmp_layout.addWidget(self.create_high_quality_video)

        nested_tmp_layout = _create_horizontal_layout()
        nested_tmp_layout.addLayout(tmp_layout)

        tmp_layout = _create_vertical_layout()
        # Bodypart list
        self.bdpt_list_widget = QtWidgets.QListWidget()
        # self.bdpt_list_widget.setMaximumWidth(500)
        self.bdpt_list_widget.addItems(self.all_bodyparts)
        self.bdpt_list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.MultiSelection
        )
        self.bdpt_list_widget.selectAll()
        self.bdpt_list_widget.setEnabled(False)
        self.bdpt_list_widget.itemSelectionChanged.connect(
            self.update_selected_bodyparts
        )
        nested_tmp_layout.addWidget(self.bdpt_list_widget)

        tmp_layout.addLayout(nested_tmp_layout)

        layout.addLayout(tmp_layout)

    def update_high_quality_video(self, s):
        if s == Qt.Checked:
            self.logger.info("High quality ENABLED.")

        else:
            self.logger.info("High quality DISABLED.")

    def update_plot_trajectory_choice(self, s):
        if s == Qt.Checked:
            self.logger.info("Plot trajectories ENABLED.")

        else:
            self.logger.info("Plot trajectories DISABLED.")

    def update_selected_bodyparts(self):
        selected_bodyparts = [
            item.text() for item in self.bdpt_list_widget.selectedItems()
        ]
        self.logger.info(f"Selected bodyparts for plotting:\n\t{selected_bodyparts}")
        self.bodyparts_to_use = selected_bodyparts

    def update_use_all_bodyparts(self, s):
        if s == Qt.Checked:
            self.bdpt_list_widget.setEnabled(False)
            self.bdpt_list_widget.selectAll()
            self.logger.info("Plot all bodyparts ENABLED.")

        else:
            self.bdpt_list_widget.setEnabled(True)
            self.logger.info("Plot all bodyparts DISABLED.")

    def update_use_filtered_data(self, state):
        if state == Qt.Checked:
            self.logger.info("Use filtered data ENABLED")
        else:
            self.logger.info("Use filtered data DISABLED")

    def update_draw_skeleton(self, state):
        if state == Qt.Checked:
            self.logger.info("Draw skeleton ENABLED")
        else:
            self.logger.info("Draw skeleton DISABLED")

    def update_overwrite_videos(self, state):
        if state == Qt.Checked:
            self.logger.info("Overwrite videos ENABLED")
        else:
            self.logger.info("Overwrite videos DISABLED")

    def update_videotype(self, vtype):
        self.logger.info(f"Looking for .{vtype} videos")
        self.filelist.clear()
        self.selected_videos_text.setText("")
        self.select_video_button.setText("Select videos")

    def update_color_by(self, text):
        self.logger.info(f"Coloring keypoints in videos by {text}")

    def update_cfg(self):
        text = self.proj_line.text()
        self.config = text

    def browse_dir(self):
        cwd = self.config
        config = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select a configuration file", cwd, "Config files (*.yaml)"
        )
        if not config[0]:
            return
        self.config = config[0]
        self.cfg_line.setText(self.config)

    def select_videos(self):
        cwd = self.config.split("/")[0:-1]
        cwd = "\\".join(cwd)
        filenames = QtWidgets.QFileDialog.getOpenFileNames(
            self,
            "Select video(s) to analyze",
            cwd,
            f"Video files (*.{self.videotype_widget.currentText()})",
        )

        if filenames:
            self.filelist.update(
                filenames[0]
            )  # Qt returns a tuple ( list of files, filetype )
            self.selected_videos_text.setText("%s videos selected" % len(self.filelist))
            self.select_video_button.setText("Add more videos")
            self.select_video_button.adjustSize()
            self.selected_videos_text.adjustSize()
            self.logger.info(f"Videos selected to analyze:\n{self.filelist}")

    def update_filter_choice(self, rb):
        if rb.text() == "Yes":
            self.filtered = True
        else:
            self.filtered = False

    def update_video_slow_choice(self, rb):
        if rb.text() == "Yes":
            self.slow = True
        else:
            self.slow = False

    def update_draw_skeleton_choice(self, rb):
        if rb.text() == "Yes":
            self.draw = True
        else:
            self.draw = False

    def create_videos(self):

        config = self.config
        shuffle = self.shuffle.value()
        trainingsetindex = self.trainingset.value()
        videos = self.filelist
        bodyparts = "all"
        videotype = self.videotype_widget.currentText()
        trailpoints = self.trail_points.value()
        color_by = self.color_by_widget.currentText()

        filtered = True
        if self.use_filtered_data_checkbox.checkState() == False:
            filtered = False

        draw_skeleton = True
        if self.draw_skeleton_checkboxx.checkState() == False:
            draw_skeleton = False

        slow_video = True
        if self.create_high_quality_video.checkState() == False:
            slow_video = False

        plot_trajectories = True
        if self.plot_trajectories.checkState() == False:
            plot_trajectories = False

        if len(self.bodyparts_to_use) != len(self.all_bodyparts):
            bodyparts = self.bodyparts_to_use

        deeplabcut.create_labeled_video(
            config=config,
            videos=videos,
            videotype=videotype,
            shuffle=shuffle,
            trainingsetindex=trainingsetindex,
            filtered=filtered,
            save_frames=slow_video,
            displayedbodyparts=bodyparts,
            draw_skeleton=draw_skeleton,
            trailpoints=trailpoints,
            color_by=color_by,
        )

        if plot_trajectories:
            deeplabcut.plot_trajectories(
                config=config,
                videos=videos,
                videotype=videotype,
                shuffle=shuffle,
                trainingsetindex=trainingsetindex,
                filtered=filtered,
                displayedbodyparts=bodyparts,
            )
