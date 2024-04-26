import os

# Takes a list of directories to create from a starting point, called output_path
def create_directories(directories, output_path):
    for directory in directories[:-1]:
        if directory:
            output_path += '/' + directory
            if not os.path.exists(output_path):
                os.makedirs(output_path)

# Takes a URL and the relative path to a resource (including backsteps '../')
# Returns the URL navigated back by the backsteps, and the relative path without backsteps
def calculate_backsteps(url, resource_path):
    back_steps = resource_path.count('../')
    resource_path = resource_path.replace('../', '')

    if not url.endswith('/'):
        back_steps += 1

    url = ('/').join(url.split('/')[:-back_steps])
    return (url, resource_path)

# Builds the path to a resource and creates the directories for the resulting path
def create_resource_directory(url, resource_path, output_path):
    path = (url + '/' + resource_path).split('//')[-1]
    create_directories(path.split('/'), output_path)