
import os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator
)
from PyQt6.QtCore import Qt
import subprocess

from scr.configWindow import *
from scr.presetmanagerWindow import *

class GameLauncher(QWidget):
    def __init__(self):

        super().__init__()
        self.mod_files = {}  # Dictionary to store {display_name: filename}
        self.mod_dependencies = {}  # Dictionary to store {mod_name: [dependencies]}
        self.default_game_root = r"C:\Program Files (x86)\Steam\steamapps\common\Victoria 2"
        self.config_file = "launcher_configs.json"
        self.game_root = self.default_game_root
        self.settings_file = os.path.join(self.game_root, "mod", self.config_file)
        self.initUI()
        self.load_mods()
        self.loadSettings()
        self.user_dir = self.mod_user_dirs.get(self.get_checked_mods()[-1], "") if self.get_checked_mods() else ""


    def initUI(self):
        self.setWindowTitle('Game Launcher')
        self.setGeometry(300, 300, 300, 400)

        layout = QVBoxLayout()

        # Mod tree structure
        self.mod_tree = QTreeWidget()
        self.mod_tree.setHeaderLabels(['Mods'])
        self.mod_tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.mod_tree.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.mod_tree)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        # Start button
        self.start_button = QPushButton('Start Game')
        self.start_button.clicked.connect(self.start_game)
        self.start_button.setFixedSize(100, 30)
        buttons_layout.addWidget(self.start_button)

        # Preset manager button
        self.preset_manager_button = QPushButton('Manage Pre-Sets')
        self.preset_manager_button.clicked.connect(self.preset_manager)
        self.preset_manager_button.setFixedSize(150, 30)
        buttons_layout.addWidget(self.preset_manager_button)

        # Configuration button to open config dialog
        self.config_button = QPushButton('Settings')
        self.config_button.clicked.connect(self.open_config_dialog)
        self.config_button.setFixedSize(100, 30)
        buttons_layout.addWidget(self.config_button)

        layout.addLayout(buttons_layout)

        buttons_layout2 = QHBoxLayout()
        buttons_layout2.addStretch()

        # Check for Updates button
        self.update_button = QPushButton('Check for Updates')
        self.update_button.setFixedSize(150, 30)
        self.update_button.clicked.connect(self.check_for_updates)
        buttons_layout2.addWidget(self.update_button)

        # About button
        self.about_button = QPushButton('About')
        self.about_button.clicked.connect(self.open_about_dialog)
        self.about_button.setFixedSize(100, 30)
        buttons_layout2.addWidget(self.about_button)

        # Quit button
        self.quit_button = QPushButton('Quit')
        self.quit_button.setFixedSize(100, 30)
        self.quit_button.clicked.connect(self.close)
        buttons_layout2.addWidget(self.quit_button)

        buttons_layout2.addStretch()

        layout.addLayout(buttons_layout2)

        self.setLayout(layout)

    def set_checked_mods(self, checked_mods):
        """Set the checked state of mods in the tree based on the provided list."""
        iterator = QTreeWidgetItemIterator(self.mod_tree, QTreeWidgetItemIterator.IteratorFlag.All)
        self.mod_tree.blockSignals(True)  # Prevent signals during setup
        while iterator.value():
            item = iterator.value()
            mod_name = item.text(0)
            if mod_name in checked_mods:
                item.setCheckState(0, Qt.CheckState.Checked)
            else:
                item.setCheckState(0, Qt.CheckState.Unchecked)
            iterator += 1
        self.mod_tree.blockSignals(False)  # Re-enable signals

    def preset_manager(self):
        """Opens the preset manager dialog."""
        dialog = PresetManagerDialog(self.get_checked_mods(), self.settings_file, parent=self)
        if dialog.exec():
            self.checked_mods = dialog.checked_mods
            self.saveSettings()  # Save the new preset

    def open_about_dialog(self):
        """Opens the about dialog."""
        # TODO: Implement the about dialog
        print("About dialog not implemented yet.")

    def check_for_updates(self):
        """Opens the about dialog."""
        # TODO: Implement the about dialog
        print("About dialog not implemented yet.")


    
    def open_config_dialog(self):
        """Opens the configuration dialog."""
        dialog = ConfigDialog(self.game_root, self)
        if dialog.exec():
            new_root = dialog.get_new_root()
            if new_root != self.game_root:
                self.game_root = new_root
                self.settings_file = os.path.join(self.game_root, "mod", self.config_file)
                self.root_label.setText(f"Game Root: {self.game_root}")
                self.load_mods()
                self.saveSettings()  # Save the new game root

    def load_mods(self):
        mod_folder = os.path.join(self.game_root, "mod")
        
        if not os.path.exists(mod_folder):
            print(f"Mod folder does not exist: {mod_folder}")
            self.mod_tree.clear()
            return

        # First pass: Load all mods and their dependencies
        self.mod_files.clear()
        self.mod_dependencies.clear()
        self.mod_user_dirs = {}
        for file in os.listdir(mod_folder):
            if file.endswith(".mod"):
                try:
                    with open(os.path.join(mod_folder, file), 'r', encoding='utf-8', errors='ignore') as mod_file:
                        content = mod_file.read()
                        name = ""
                        dependencies = []
                        user_dir = ""
                        for line in content.split('\n'):
                            if line.startswith("name"):
                                name = line.split("=")[1].strip().strip('"')
                            elif line.startswith("dependencies"):
                                deps_str = line.split("=")[1].strip().strip("{}")
                                dependencies = [dep.strip().strip('"') for dep in deps_str.split(",") if dep.strip()]
                            elif line.startswith("user_dir"):
                                user_dir = line.split("=")[1].strip().strip('"')
                        
                        if name:
                            self.mod_files[name] = file
                            self.mod_dependencies[name] = dependencies
                            self.mod_user_dirs[name] = user_dir
                except Exception as e:
                    print(f"Error reading mod file {file}: {e}")

        # Second pass: Create tree structure
        self.mod_tree.blockSignals(True)  # Prevent signals during setup
        self.mod_tree.clear()
        mod_items = {}

        # Create all mod items first
        for mod_name in self.mod_files.keys():
            item = QTreeWidgetItem()
            item.setText(0, mod_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            mod_items[mod_name] = item

        # Organize mods based on dependencies
        for mod_name, dependencies in self.mod_dependencies.items():
            if dependencies:
                for dep in dependencies:
                    if dep in mod_items:
                        mod_items[dep].addChild(mod_items[mod_name])
                        break  # Assume first dependency as parent
                else:
                    # No valid dependency found, add as top-level
                    self.mod_tree.addTopLevelItem(mod_items[mod_name])
            else:
                # No dependencies, add as top-level
                self.mod_tree.addTopLevelItem(mod_items[mod_name])

        self.mod_tree.expandAll()
        self.mod_tree.blockSignals(False)  # Re-enable signals

    def get_checked_mods(self):
        checked_mods = []
        last_user_dir_mod = None
        iterator = QTreeWidgetItemIterator(self.mod_tree, QTreeWidgetItemIterator.IteratorFlag.All)
        while iterator.value():
            item = iterator.value()
            if item.checkState(0) == Qt.CheckState.Checked:
                mod_name = item.text(0)
                if mod_name in self.mod_files:
                    checked_mods.append(mod_name)
                    if self.mod_user_dirs[mod_name]:
                        last_user_dir_mod = mod_name
            iterator += 1
        if last_user_dir_mod:
            self.user_dir = self.mod_user_dirs[last_user_dir_mod]
            print(f"User directory: {self.user_dir}")
        else:
            self.user_dir = ""
        return checked_mods


    def start_game(self):
        selected_mods = self.get_checked_mods()
        
        if selected_mods:
            mod_files = [f"-mod=mod/{self.mod_files[mod]}" for mod in selected_mods]
            mods_argument = " ".join(mod_files)
            command = f'cd "{self.game_root}" && v2game.exe {mods_argument}'
            print(f"Starting game with command: {command}")
            subprocess.run(command, shell=True)
            self.saveSettings()
        else:
            print("No mods selected. Starting game without mods.")
            command = f'cd "{self.game_root}" && v2game.exe'
            subprocess.run(command, shell=True)

    def on_item_changed(self, item, column):
        if column == 0:
            # Get checked state of the mod item
            check_state = item.checkState(0)
            
            # Prevent automatic selection/deselection of children
            self.mod_tree.blockSignals(True)
            
            # Save current settings
            self.saveSettings()
            
            # Re-enable signals after making the change
            self.mod_tree.blockSignals(False)

    def loadSettings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    checked_mods = settings.get('checked_mods', [])
                    self.game_root = settings.get('game_root', self.default_game_root)
            except Exception as e:
                print(f"Error loading settings: {e}")
                checked_mods = []
        else:
            checked_mods = []

        self.load_mods()

        # Apply checked mods
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    checked_mods = settings.get('checked_mods', [])
            except Exception as e:
                print(f"Error reading checked mods from settings: {e}")
                checked_mods = []

            iterator = QTreeWidgetItemIterator(self.mod_tree, QTreeWidgetItemIterator.IteratorFlag.All)
            self.mod_tree.blockSignals(True)  # Prevent signals during setup
            while iterator.value():
                item = iterator.value()
                mod_name = item.text(0)
                if mod_name in checked_mods:
                    item.setCheckState(0, Qt.CheckState.Checked)
                else:
                    item.setCheckState(0, Qt.CheckState.Unchecked)
                iterator += 1
            self.mod_tree.blockSignals(False)  # Re-enable signals

    def saveSettings(self):
        checked_mods = self.get_checked_mods()
        settings = {}
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            except Exception as e:
                print(f"Error reading settings: {e}")
        settings['checked_mods'] = checked_mods
        try:
            mod_folder = os.path.join(self.game_root, "mod")
            os.makedirs(mod_folder, exist_ok=True)
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            print("Settings saved successfully.")
        except Exception as e:
            print(f"Error saving settings: {e}")
      