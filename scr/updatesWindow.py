import os
import requests
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QListWidgetItem
from PyQt6.QtCore import Qt
from datetime import datetime
import webbrowser

class UpdateCheckerDialog(QDialog):
    def __init__(self, mod_files, mod_folder, parent=None):
        super().__init__(parent)
        self.mod_files = mod_files
        self.mod_folder = mod_folder
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Mod Update Checker")
        self.setFixedSize(500, 200)
        layout = QVBoxLayout()

        self.status_label = QLabel("Checking for updates...")
        layout.addWidget(self.status_label)

        self.mod_list = QListWidget()
        layout.addWidget(self.mod_list)

        self.ok_button = QPushButton("Close")
        self.ok_button.clicked.connect(self.close)
        layout.addWidget(self.ok_button)

        self.setLayout(layout)

        self.mod_list.itemClicked.connect(self.on_item_clicked)

        self.check_for_updates()

    def check_for_updates(self):
        mods_with_updates = []
        for mod_name, mod_info in self.mod_files.items():
            github_url = mod_info.get('github')
            current_release = mod_info.get('current_release')
            mod_file_path = os.path.join(self.mod_folder, mod_info['file'])

            if github_url:
                try:
                    # Check for latest release
                    release_api_url = github_url.replace("github.com", "api.github.com/repos") + "/releases/latest"
                    release_response = requests.get(release_api_url)
                    latest_release_info = {}
                    latest_release_tag = None
                    latest_release_date = None
                    if release_response.status_code == 200:
                        latest_release_info = release_response.json()
                        latest_release_tag = latest_release_info.get('tag_name', None)
                        latest_release_date = latest_release_info.get('published_at', None)

                    # Check for latest commit
                    commit_api_url = github_url.replace("github.com", "api.github.com/repos") + "/commits"
                    commit_response = requests.get(commit_api_url)
                    latest_commit_date = None
                    if commit_response.status_code == 200:
                        latest_commit_info = commit_response.json()
                        latest_commit_date = latest_commit_info[0]['commit']['committer']['date']

                    # Check modification date of local mod file
                    mod_last_modified_timestamp = os.path.getmtime(mod_file_path)
                    mod_last_modified_date = datetime.utcfromtimestamp(mod_last_modified_timestamp)

                    has_new_release = False
                    has_new_commit = False
                    # Compare release date
                    if latest_release_date:
                        latest_release_date = datetime.strptime(latest_release_date, "%Y-%m-%dT%H:%M:%SZ")
                        if (latest_release_tag and latest_release_tag != current_release) or latest_release_date>mod_last_modified_date:
                            has_new_release = True
                    
                    # Compare commit date
                    if latest_commit_date:
                        latest_commit_date = datetime.strptime(latest_commit_date, "%Y-%m-%dT%H:%M:%SZ")
                        if latest_commit_date > mod_last_modified_date:
                            has_new_commit = True

                    if has_new_release and has_new_commit:
                        mods_with_updates.append((f"{mod_name} - New packed release, {latest_release_tag}, and new commits avaliable.", github_url))
                    elif has_new_release:
                        mods_with_updates.append((f"{mod_name} - New packed release available: {latest_release_tag}", github_url))
                    elif has_new_commit:
                        mods_with_updates.append((f"{mod_name} - New commits avaliable.", github_url))

                except Exception as e:
                    self.status_label.setText(f"An error occurred while displaying the updates, report it to Wyrm on the discord server: {e}")

        if mods_with_updates:
            try:
                self.mod_list.clear()
                for update_text, url in mods_with_updates:
                    item = QListWidgetItem(update_text)
                    if url:
                        item.setData(Qt.ItemDataRole.UserRole, url)
                    self.mod_list.addItem(item)
                self.status_label.setText("Updates found for the following mods (Click to go to the download page):")
            except Exception as e:
                self.status_label.setText(f"An error occurred while displaying the updates, report it to Wyrm on the discord server: {e}")
        else:
            self.status_label.setText("All mods are up to date.")

    def on_item_clicked(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            webbrowser.open(url)