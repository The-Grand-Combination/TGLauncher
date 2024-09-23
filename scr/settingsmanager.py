import os
class SettingsManager:
    def __init__(self, settings_file):
        self.settings_file = settings_file
        self.settings = {}
        self.load_settings()

    def load_settings(self):
        """Loads settings from the file into a dictionary."""
        if not os.path.exists(self.settings_file):
            # Create the settings file with default values if it doesn't exist
            self.create_default_settings()
        
        self.settings = {}
        with open(self.settings_file, 'r') as file:
            current_category = None
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):  # Skip empty lines or comments
                    continue
                if '=' not in line:  # If no '=', assume it's a category header
                    current_category = line.strip('[]')
                    self.settings[current_category] = {}
                else:  # Parse key-value pairs
                    key, value = line.split('=', 1)
                    key, value = key.strip(), value.strip()
                    if current_category:
                        self.settings[current_category][key] = value

    def get_setting(self, category, key, default=None):
        """Returns the value of a specific setting, or a default if not found."""
        return self.settings.get(category, {}).get(key, default)

    def save_settings(self, updated_settings):
        """Saves the updated settings by replacing existing entries."""
        self.load_settings()  # Reload settings to get the latest state

        # Update the settings with the new values
        for key, value in updated_settings.items():
            for category, items in self.settings.items():
                if key in items:
                    self.settings[category][key] = str(value)

        # Save the updated settings back to the file
        with open(self.settings_file, 'w') as file:
            for category, items in self.settings.items():
                file.write(f'[{category}]\n')
                for key, value in items.items():
                    file.write(f'{key}={value}\n')

    def create_default_settings(self):
        """Creates the settings file with default values."""
        default_settings = """[graphics]
                            x=1920
                            y=1080
                            fullScreen=no
                            borderless=yes

                            [sound]
                            master_volume=50
                            sound_fx_volume=50
                            music_volume=50

                            [gui]
                            lastplayer=Player

                            [general]
                            debug_saves=0
                            autosave=YEARLY
                            update_time=1.000000
                            """
        with open(self.settings_file, 'w') as file:
            file.write(default_settings)

    def update_setting_in_file(self, category, key, value):
        """Updates a specific setting in the file without altering others."""
        self.settings[category][key] = value
        self.save_settings(self.settings)
