

import yaml
import os

class SecretsManager:

    def __init__(self, file_path="secrets.yml") -> None:
        self.secrets = {}
        self.file_path=file_path

        if os.path.exists(file_path):
            print(f"Loading secrets from {self.file_path}")
            self.secrets = self.read_yaml_file()
        else:
            print(f"No secrets file found, creating a new one.")
            self.create_empty_file()

    def read_yaml_file(self):
        with open(self.file_path, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
        return (data or {})
    
    def create_empty_file(self):
        with open(self.file_path, 'w'):
            pass
    
    def save_to_file(self):
        with open(self.file_path, 'w') as yaml_file:
            yaml.dump(self.secrets, yaml_file, default_flow_style=False)

    def set(self, key, value):
        self.secrets[key] = value
        self.save_to_file()

    def get(self, key):
        return self.secrets.get(key)


    # # Example usage
    # read_values = read_yaml_file(PATH)

    # if read_values:
    #     for key, value in read_values.items():
    #         print(f"{key}: {value}")
    # else:
    #     print("No values found in the YAML file.")
