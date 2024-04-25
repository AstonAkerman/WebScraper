import os
import requests

def create_directories(directories, output_path):
    for directory in directories[:-1]:
        if directory:
            output_path += '/' + directory
            if not os.path.exists(output_path):
                os.makedirs(output_path)

def calculate_backsteps(url, resource_path):
    back_steps = resource_path.count('../')
    resource_path = resource_path.replace('../', '')

    if not url.endswith('/'):
        back_steps += 1

    url = ('/').join(url.split('/')[:-back_steps])
    return (url, resource_path)

def create_resource_directory(url, resource_path, output_path):
    path = (url + '/' + resource_path).split('//')[-1]
    create_directories(path.split('/'), output_path)