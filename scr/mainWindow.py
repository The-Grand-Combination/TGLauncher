
import os
import json
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QLabel,
    QPushButton, QTreeWidget, QTreeWidgetItem, QTreeWidgetItemIterator
)
from PyQt6.QtCore import Qt
import subprocess
import threading

from PyQt6.QtGui import QIcon


from scr.configWindow import *
from scr.presetmanagerWindow import *
from scr.updatesWindow import *

class GameLauncher(QWidget):
    def __init__(self):

        super().__init__()
        self.setWindowIcon(QIcon('scr/icon.ico'))

        self.mod_files = {}  # Dictionary to store {display_name: filename}
        self.mod_dependencies = {}  # Dictionary to store {mod_name: [dependencies]}
        self.default_game_roots = [
            os.path.join(os.path.dirname(__file__), "v2game.exe"),
            r"C:\Program Files (x86)\Steam\steamapps\common\Victoria 2",
            r"C:\GOG Games\Victoria II"
        ]
        self.game_root = None
        for game_root in self.default_game_roots:
            if os.path.exists(os.path.join(game_root, "v2game.exe")):
                self.game_root = game_root
                break
        if not self.game_root:
            QMessageBox.critical(self, "Error", "Could not find the game executable. Place this launcher inside your Victoria 2 installation folder.")
            sys.exit(1)
        self.config_file = "launcher_configs.json"
        self.settings_file = os.path.join(self.game_root, "mod", self.config_file)
        self.initUI()
        self.load_mods()
        self.loadSettings()

    def initUI(self):
        self.setWindowTitle('The Greater Launcher')
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
        try:
            dialog = PresetManagerDialog(self.get_checked_mods(), self.settings_file, parent=self)
            
            if dialog.exec():
                self.checked_mods = dialog.checked_mods
                self.set_checked_mods(self.checked_mods)  # Apply the preset to the tree
                
                # Update the user_dir based on the newly checked mods
                self.get_checked_mods()  # This will update the user_dir based on the checked mods
                
                self.saveSettings()  # Save the new preset
        except Exception as e:
            QMessageBox.warning(self, 'Error', f"Error occurred in preset manager: {e}")

    def open_about_dialog(self):
        """Opens the about dialog with GitHub and Discord links."""
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("About TGLauncher")
        about_dialog.setFixedSize(300, 200)

        # Main layout (centered vertically and horizontally)
        main_layout = QVBoxLayout(about_dialog)

        # Create a label with rich text for clickable links, centered
        about_text = QLabel(
            "<h3 style='text-align: center;'>The Greater Launcher</h3>"
            "<p style='text-align: center;'>Developed by the TGC Modding Team.</p>"
            "<p style='text-align: center;'><a href='https://github.com/The-Grand-Combination/TGLauncher'>GitHub Repository</a><br>"
            "<a href='https://discord.gg/the-grand-combination-689466155978588176'>Join us on Discord</a></p>"
        )
        about_text.setTextFormat(Qt.TextFormat.RichText)
        about_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        about_text.setOpenExternalLinks(True)
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the text

        # Add the label to the main layout
        main_layout.addWidget(about_text)

        # Create a horizontal layout to center the OK button
        button_layout = QHBoxLayout()
        close_button = QPushButton("OK")
        close_button.setFixedSize(80, 30)
        close_button.clicked.connect(about_dialog.accept)

        # Add the button to the button layout and center it
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        button_layout.addStretch()

        # Add button layout to the main layout
        main_layout.addLayout(button_layout)

        about_dialog.exec()


    def check_for_updates(self):
        dialog = UpdateCheckerDialog(self.mod_files, os.path.join(self.game_root, "mod"))
        dialog.exec()


    def open_config_dialog(self):
        """Opens the configuration dialog."""
        try:
            dialog = ConfigDialog(self.game_root, self, self.user_dir)
            if dialog.exec():
                self.settings_file = os.path.join(self.game_root, "mod", self.config_file)
                self.load_mods()
                self.saveSettings()  # Save the new game root
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error occurred in configuration dialog: {e}")

    def load_mods(self):
        mod_folder = os.path.join(self.game_root, "mod")
        
        if not os.path.exists(mod_folder):
            print(f"Mod folder does not exist: {mod_folder}")
            self.mod_tree.clear()
            return

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
                        github = ""
                        version = ""
                        for line in content.split('\n'):
                            if line.startswith("name"):
                                name = line.split("=")[1].strip().strip('"')
                            elif line.startswith("dependencies"):
                                deps_str = line.split("=")[1].strip().strip("{}")
                                dependencies = [dep.strip().strip('"') for dep in deps_str.split(",") if dep.strip()]
                            elif line.startswith("user_dir"):
                                user_dir = line.split("=")[1].strip().strip('"')
                            elif line.startswith("github"):
                                github = line.split("=")[1].strip().strip('"')
                            elif line.startswith("version"):
                                version = line.split("=")[1].strip().strip('"')

                        if name:
                            self.mod_files[name] = {
                                'file': file,
                                'github': github if github else None,
                                'release': version if version else None
                            }
                            self.mod_dependencies[name] = dependencies
                            self.mod_user_dirs[name] = user_dir
                except Exception as e:
                    print(f"Error reading mod file {file}: {e}")

        self.mod_tree.blockSignals(True)
        self.mod_tree.clear()
        mod_items = {}

        for mod_name in self.mod_files.keys():
            item = QTreeWidgetItem()
            item.setText(0, mod_name)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            item.setCheckState(0, Qt.CheckState.Unchecked)
            mod_items[mod_name] = item

        for mod_name, dependencies in self.mod_dependencies.items():
            if dependencies:
                for dep in dependencies:
                    if dep in mod_items:
                        mod_items[dep].addChild(mod_items[mod_name])
                        break
                else:
                    self.mod_tree.addTopLevelItem(mod_items[mod_name])
            else:
                self.mod_tree.addTopLevelItem(mod_items[mod_name])

        self.mod_tree.expandAll()
        self.mod_tree.blockSignals(False)

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
            mod_files = [f"-mod=mod/{self.mod_files[mod]['file']}" for mod in selected_mods]
            mods_argument = " ".join(mod_files)
            command = f'cd "{self.game_root}" && v2game.exe {mods_argument}'
            print(f"Starting game with command: {command}")
            thread = threading.Thread(target=subprocess.run, args=(command, ), kwargs={'shell': True})
            thread.start()
            self.saveSettings()
            self.close()
        else:
            print("No mods selected. Starting game without mods.")
            command = f'cd "{self.game_root}" && v2game.exe'
            thread = threading.Thread(target=subprocess.run, args=(command, ), kwargs={'shell': True})
            thread.start()
            self.close()

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
        checked_mods = []
        
        # Load settings from the file if it exists
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    checked_mods = settings.get('checked_mods', [])
                    self.game_root = settings.get('game_root', self.game_root)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Load mods into the tree
        self.load_mods()
        
        # Apply checked mods
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
        
        # Set the user_dir based on the checked mods at startup
        self.get_checked_mods()  # This will update the user_dir based on the checked mods


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
