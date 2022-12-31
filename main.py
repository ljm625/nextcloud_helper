import json
import re

import yaml
import subprocess
import os
rescan_command = "{php_path} {occ_path} files:scan --path={dir}"
preview_generate_command = "{php_path} {occ_path} preview:generate-all --path={dir}"
memories_command = "{php_path} {occ_path} memories:index"

def load_config(name):
    with open(name) as file:
        config = yaml.load(file.read(),Loader = yaml.FullLoader)
        return config

def load_folder_data():
    try:
        with open("/tmp/nextcloud_scan_info.json") as file:
            scan_info = json.load(file)
            return scan_info
    except Exception as e:
        print(f"Error: {e}")
        return {}

def save_folder_data(data):
    with open("/tmp/nextcloud_scan_info.json", "w+") as file:
        json.dump(data,file)


def validate_path(chname):
    for achar in ("'",'"','*','?','~','`','!','#','$','&','|','{','}',';','<','>','^',' ','(',')','[',']'):
        chname = chname.replace(achar,'\\' + achar)
    return chname



def check_for_changes(path):
    regex = r" *\| *([0-9]+) *\| *([0-9]+) *\| *([0-9\:]+)"
    rescan = False
    output = execute_command(rescan_command.format(php_path=config["php_path"],occ_path=config["occ_path"],dir=validate_path(path)))
    if output:
        output_lines = output.split("\n")
        for line in output_lines:
            result = re.match(regex,line)
            if result:
                folders = int(result.group(1))
                files = int(result.group(2))
                print(f"Path: {path} Folders: {folders} Files: {files}")
                if scan_data.get(path):
                    if files > scan_data[path]:
                        rescan = True
                        print(f"Path: {path} Rescan needed")
                scan_data[path] = files
        return rescan
    else:
        print(f"Issue on Executing rescan on folder {path}, please check")
        return rescan

def generate_preview(path):
    output = execute_command(preview_generate_command.format(php_path=config["php_path"],occ_path=config["occ_path"],dir=validate_path(path)))
    if output:
        return True
    else:
        print(f"Issue on Generating Preview on folder {path}, please check")
        return False

def generate_memories_index():
    output = execute_command(memories_command.format(php_path=config["php_path"],occ_path=config["occ_path"]))
    if output:
        return True
    else:
        print(f"Issue on Generating Memories, please check")
        return False



def execute_command(command):
    try:
        (status,output) = subprocess.getstatusoutput(command)
        if status !=0:
            raise Exception(f"Status code: {status}, Return: {output}")
        print(output)
        return output
    except Exception as e:
        print(e)
        return None
if __name__ == '__main__':
    print("Starting to run jobs")
    config = load_config("config.yaml")
    scan_data = load_folder_data()
    memories_re_index = False
    for path in config["scan_paths"]:
        if check_for_changes(path):
            if config["enable_preview_generate"]:
                generate_preview(path)
            memories_re_index = True
    if memories_re_index and config["enable_memories"]:
        generate_memories_index()
    save_folder_data(scan_data)
    print("All Done")





