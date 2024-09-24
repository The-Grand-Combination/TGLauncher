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
        default_settings = """gui=
        {
        language=l_english
        }
        graphics=
        {
        size=
        {
            x=1920
            y=1080
        }

        refreshRate=60
        fullScreen=no
        borderless=yes
        shadows=no
        shadowSize=2048
        multi_sampling=0
        anisotropic_filtering=0
        gamma=50.000000
        }
        sound_fx_volume=36.000000
        music_volume=52.000000
        scroll_speed=50.000000
        camera_rotation_speed=50.000000
        zoom_speed=50.000000
        mouse_speed=50.000000
        master_volume=28.000000
        ambient_volume=43.000000
        mapRenderingOptions=
        {
        renderTrees=yes
        onmap=yes
        simpleWater=no
        counter_distance=300.000000
        text_height=300.000000
        sea_text_alpha=120
        details=1.000
        }
        lastplayer=Player
        lasthost=""
        serveradress="diplomacy.valkyrienet.com"
        debug_saves=0
        autosave=YEARLY
        simple=no
        categories=
        {
        1 1 1 1 1 1 }
        update_time=1.000000
        shortcut=yes

        """
        with open(self.settings_file, 'w') as file:
            file.write(default_settings)

    def update_setting_in_file(self, category, key, value):
        """Updates a specific setting in the file without altering others."""
        self.settings[category][key] = value
        self.save_settings(self.settings)
