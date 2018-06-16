#!/usr/bin/env python
import json
import os
import shutil
import re
import markdown2
import copy

color_green = '\033[0;32m{0}\033[0;0m'
color_red = '\033[1;31m{0}\033[0;0m'

class WebsiteBuilder:

    def __init__(self):
        # Change working directory to current directory
        working_directory = os.getcwd()
        os.chdir(working_directory)

        # Load the configuration file
        self.config = Config()
        self.config.parse_file()

    def build(self):
        # Destroy old destination folder
        if os.path.exists(self.config.build_folder):
            print 'Deleting old folder...'
            shutil.rmtree(self.config.build_folder)
            print color_green.format('Old build folder deleted')

        # Copy files
        print 'Copying files...'
        for copy in self.config.copies:
            copy.copy(self.config.build_folder)

        # Build files
        print 'Building files...'
        for build in self.config.builds:
            build.build()

class Config:
    config = []
    build_folder = 'dist/'
    start_tag = '<!--'
    end_tag = '-->'
    copies = []
    builds = []

    def __init__(self):
        print 'Loading configuration file...'
        if os.path.exists('builder.json'):
            self.config = json.load(open('builder.json', 'r'))
            print color_green.format('Configuration file loaded')
        else:
            print color_red.format('Configuration file not found, make sure you are in the correct folder')
            exit()

    def parse_file(self):
        if 'config' in self.config:
            self.parse_config(self.config['config'])
        if 'copy' in self.config:
            self.parse_copy(self.config['copy'])
        if 'build' in self.config:
            self.parse_build(self.config['build'])

    def parse_config(self, configs):
        if 'build_folder' in configs:
            self.build_folder = configs['build_folder']
        if 'start_tag' in configs:
            self.start_tag = configs['start_tag']
        if 'end_tag' in configs:
            self.end_tag = configs['end_tag']

    def parse_copy(self, copies):
        for copy in copies:
            self.copies.append(Copy(copy))

    def parse_build(self, builds):
        for build in builds:
            self.builds.append(Build(self, ResultFile(self), build))

class Copy:

    def __init__(self, copy):
        self.path_from = copy['from']
        self.path_to = copy['to']

    def copy(self, build_folder):
        if os.path.exists(self.path_from):
            if os.path.isdir(self.path_from):
                shutil.copytree(self.path_from, build_folder + self.path_to)
                print color_green.format('Folder ' + self.path_from + ' copied')
            else:
                shutil.copy(self.path_from, build_folder + self.path_to)
                print color_green.format('File ' + self.path_from + ' copied')
        else:
            print color_red.format('File ' + self.path_from + ' not found')

class Build:

    def __init__(self, config, result, build):
        self.config = config
        self.result = copy.deepcopy(result)

        self.path = build['path']
        self.raw_contents = ''
        self.contents = []
        if 'contents' in build:
            self.raw_contents = build['contents']
            self.parse_content(build['contents'])

    def parse_content(self, contents):
        for content in contents:
            self.contents.append(Build(self.config, self.result, content))

    def build(self):
        if os.path.isdir(self.path):
            self.build_folder()
        else:
            self.build_file()

    def build_folder(self):
        paths = os.listdir(self.path)
        for path in paths:
            new_build = Build(self.config, self.result, {'path': os.path.join(self.path, path)})
            new_build.build()

    def build_file(self):
        if os.path.exists(self.path):
            file_content = open(self.path, 'r').read()
            file_format = os.path.splitext(self.path)[1]

            self.result.insert(file_content, file_format)

            if self.contents:
                for content in self.contents:
                    new_build = {
                        'path': content.path
                    }
                    if content.contents:
                        new_build['contents'] = content.raw_contents
                    Build(self.config, self.result, new_build).build()
            else:
                self.result.save(self.path)
        else:
            print color_red.format('File ' + self.path + ' not found')

class ResultFile:

    def __init__(self, config):
        self.content = ''
        self.config = config

    def insert(self, new_content, file_format):
        if self.content:
            replace = re.findall(self.config.start_tag + ' (\w+) ' + self.config.end_tag, self.content)
            for tag in replace:
                delimiter = self.config.start_tag+' '+tag+' '+self.config.end_tag

                match = re.search(delimiter+'(.*)'+delimiter, new_content, re.S)
                if match:
                    text = match.group(1)

                    if file_format == '.md':
                        text = markdown2.markdown(text).encode('utf8', 'ignore').strip()

                    self.content = re.sub(delimiter, text, self.content)
        else:
            self.content = new_content

    def save(self, current_path):
        file_name = os.path.splitext(current_path)[0] + '.html'
        result_path = self.config.build_folder + file_name
        if not os.path.exists(os.path.dirname(result_path)):
            os.makedirs(os.path.dirname(result_path))

        result = open(result_path, 'w')
        result.write(self.content)
        result.close()

        print color_green.format('File ' + file_name + ' builded')


builder = WebsiteBuilder()
builder.build()