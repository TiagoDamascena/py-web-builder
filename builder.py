#!/usr/bin/env python
import json
import os
import shutil
import re
import markdown2

color_green = '\033[0;32m{0}\033[0;0m'
color_red = '\033[1;31m{0}\033[0;0m'

# Change working directory to current directory
working_directory = os.getcwd()
os.chdir(working_directory)

# Load the configuration file
print 'Loading configuration file...'
if os.path.exists('builder.json'):
    config = json.load(open('builder.json', 'r'))
    print color_green.format('Configuration file loaded')
    destination_folder = config['config']['build_folder']
else:
    print color_red.format('Configuration file not found, make sure you are in the correct folder')
    exit()

def copy_files(copy_from, copy_to):
    if os.path.exists(copy_from):
        if os.path.isdir(copy_from):
            shutil.copytree(copy_from, destination_folder + copy_to)
            print color_green.format('Folder ' + copy_from + ' copied')
        else:
            shutil.copy(copy_from, destination_folder + copy_to)
            print color_green.format('File ' + copy_from + ' copied')
    else:
        print color_red.format('File '+copy_from+' not found')

def build_files(current_content, current_path, content=None):
    if os.path.isdir(current_path):
        paths = os.listdir(current_path)
        for path in paths:
            build_files(current_content, os.path.join(current_path, path), content)
    else:
        if os.path.exists(current_path):
            file_content = open(current_path, 'r').read()
            file_format = os.path.splitext(current_path)[1]

            if current_content:
                replace = re.findall(r'{{(\w+)}}', current_content)
                for tag in replace:
                    text = re.search(r'{{' + tag + '}}(.*){{' + tag + '}}', file_content, re.S)
                    if text:
                        trimmed_content = text.group(1)
                    else:
                        trimmed_content = file_content

                    if file_format == '.md':
                        trimmed_content = markdown2.markdown(trimmed_content).encode('utf8', 'ignore').strip()

                    current_content = re.sub(r'{{' + tag + '}}', trimmed_content, current_content)
            else:
                current_content = file_content

            if content:
                for new_content in content:
                    if 'content' in new_content:
                        next_content = new_content['content']
                    else:
                        next_content = None

                    build_files(current_content, new_content['path'], next_content)
            else:
                file_name = os.path.splitext(current_path)[0] + '.html'
                result_path = destination_folder + file_name
                if not os.path.exists(os.path.dirname(result_path)):
                    os.makedirs(os.path.dirname(result_path))

                result = open(result_path, 'w')
                result.write(current_content)
                result.close()

                print color_green.format('File ' + file_name + ' builded')
        else:
            print color_red.format('File '+current_path+' not found')

# Destroy old destination folder
if os.path.exists(destination_folder):
    shutil.rmtree(destination_folder)

# Copy selected files
copy_config = config['copy']
print 'Copying files...'
for copy in copy_config:
    copy_files(copy['from'], copy['to'])

# Build pages from templates
build_config = config['build']
print 'Building files...'
for build in build_config:
    build_files('', build['path'], build['content'])

print color_green.format('Project builded successfully!')