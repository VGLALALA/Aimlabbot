import configparser


class ConfigReader:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

        self.activation_hotkey = self.get_int('Settings', 'ACTIVATION_HOTKEY')
        self.exit_hotkey = self.get_int('Settings', 'EXIT_HOTKEY')
        self.moveleft_hotkey = self.get_int('Settings', 'MOVELEFT_HOTKEY')
        self.moveright_hotkey = self.get_int('Settings', 'MOVERIGHT_HOTKEY')
        self.moveup_hotkey = self.get_int('Settings', 'MOVEUP_HOTKEY')
        self.movedown_hotkey = self.get_int('Settings', 'MOVEDOWN_HOTKEY')
        self.auto_deactivate_after = self.get_int('Settings', 'AUTO_DEACTIVATE_AFTER')
        self.screenshots_folder = self.config.get('Settings', 'SCREENSHOTS_FOLDER')
        self.shoot = self.config.getboolean('Settings', '_shoot')
        self.show_cv2 = self.config.getboolean('Settings', '_show_cv2')
        self.write_cv2 = self.config.getboolean('Settings', '_write_cv2')
        self.show_fps = self.config.getboolean('Settings', '_show_fps')

        self.pause = self.config.getfloat('Timing', '_pause')
        self.shoot_interval = self.config.getfloat('Timing', '_shoot_interval')


        self.ret = self.config.get('Window', '_ret')
        self.aim = self.config.getboolean('Aim', '_aim')
        self.activation_time = self.get_int('Aim', '_activation_time')

    def get_int(self, section, option):
        value = self.config.get(section, option)
        return int(value.split('#')[0].strip())

    def get_float(self, section, option):
        value = self.config.get(section, option)
        return float(value.split('#')[0].strip())

    def __str__(self):
        return f"""Configuration:
        ACTIVATION_HOTKEY: {self.activation_hotkey}
        EXIT_HOTKEY: {self.exit_hotkey}
        MOVELEFT_HOTKEY: {self.moveleft_hotkey}
        MOVERIGHT_HOTKEY: {self.moveright_hotkey}
        MOVEUP_HOTKEY: {self.moveup_hotkey}
        MOVEDOWN_HOTKEY: {self.movedown_hotkey}
        AUTO_DEACTIVATE_AFTER: {self.auto_deactivate_after}
        SCREENSHOTS_FOLDER: {self.screenshots_folder}
        _shoot: {self.shoot}
        _show_cv2: {self.show_cv2}
        _write_cv2: {self.write_cv2}
        _show_fps: {self.show_fps}
        _pause: {self.pause}
        _shoot_interval: {self.shoot_interval}
        _ret: {self.ret}
        _aim: {self.aim}
        _activation_time: {self.activation_time}
        """

if __name__ == "__main__":
    config_reader = ConfigReader('config.ini')
    print(config_reader)