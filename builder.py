#!/usr/bin/env python
import json
import os
import shutil
import re
import markdown2

color_green = '\033[0;32m{0}\033[0;0m'
color_red = '\033[1;31m{0}\033[0;0m'

class WebsiteBuilder:
    def __init__(self):
        # Change working directory to current directory
        working_directory = os.getcwd()
        os.chdir(working_directory)

        # Load the configuration file
        self.config = Config()

    def build(self):
        # Destroy old destination folder
        if os.path.exists(self.config.build_folder):
            print 'Deleting old folder...'
            shutil.rmtree(self.config.build_folder)
            print color_green.format('Old build folder deleted')

        # Copy files
        print 'Copying files...'
        for copy in self.config.copies:
            copy.copy()

        # Build files
        print 'Building files...'
        for build in self.config.builds:
            build.build()

class Config:
    def __init__(self):
        self.file_name = 'web-builder.json'

        self.build_folder = 'dist/'
        self.copies = []
        self.builds = []

        file_content = self.load_config()
        self.parse_file(file_content)

    def load_config(self):
        print 'Loading configuration file...'
        if os.path.exists(self.file_name):
            file_content = json.load(open(self.file_name, 'r'))
            print color_green.format('Configuration file loaded')
            return file_content
        else:
            print color_red.format('Configuration file not found, make sure you are in the correct directory')
            exit()

    def parse_file(self, file_content):
        if 'config' in file_content:
            self.parse_config(file_content['config'])
        if 'copy' in file_content:
            self.parse_copy(file_content['copy'])
        if 'build' in file_content:
            self.parse_build(file_content['build'])

    def parse_config(self, configs):
        if 'build_folder' in configs:
            self.build_folder = configs['build_folder']

    def parse_copy(self, copies):
        for path in copies:
            self.copies.append(Copy(self, path))

    def parse_build(self, builds):
        for path in builds:
            self.builds.append(Build(self, path))

class Copy:
    def __init__(self, config, path):
        self.config = config
        self.path = path

    def copy(self):
        if os.path.exists(self.path):
            if os.path.isdir(self.path):
                shutil.copytree(self.path, os.path.join(self.config.build_folder, self.path))
                print color_green.format('Folder ' + self.path + ' copied')
            else:
                shutil.copy(self.path, os.path.join(self.config.build_folder, self.path))
                print color_green.format('File ' + self.path + ' copied')
        else:
            print color_red.format('File ' + self.path + ' not found')

class Build:
    def __init__(self, config, path):
        self.config = config
        self.path = path

    def build(self):
        if os.path.isdir(self.path):
            self.build_folder()
        else:
            self.build_file()

    def build_folder(self):
        paths = os.listdir(self.path)
        for file_path in paths:
            new_build = Build(self.config, os.path.join(self.path, file_path))
            new_build.build()

    def build_file(self):
        if os.path.exists(self.path):
            builder = FileBuilder(self.path, self.config)
            file_content = builder.build()
            self.save(file_content)
        else:
            print color_red.format('File ' + self.path + ' not found')
            return None

    def save(self, content):
        file_name = os.path.splitext(self.path)[0] + '.html'
        result_path = os.path.join(self.config.build_folder, file_name)
        if not os.path.exists(os.path.dirname(result_path)):
            os.makedirs(os.path.dirname(result_path))

        result = open(result_path, 'w')
        result.write(content)
        result.close()

        print color_green.format('File ' + self.path + ' builded')

class FileBuilder:
    def __init__(self, path, config):
        self.path = path
        self.config = config

    def build(self):
        file_content = open(self.path, 'r').read()

        file_format = os.path.splitext(self.path)[1]
        if file_format == '.md':
            file_content = markdown2.markdown(file_content).encode('utf8', 'ignore').strip()

        template_path = self.get_template(file_content)
        if template_path:
            if os.path.exists(template_path):
                file_builder = FileBuilder(template_path, self.config)
                template_content = file_builder.build()

                return self.replace_content(template_content, file_content)
            else:
                print color_red.format('Template ' + template_path + ' not found')
                return None
        else:
            return file_content

    def get_template(self, file_content):
        match = re.search("<!-- pwb:extends\('(.+)'\) -->", file_content)
        if match:
            return match.group(1)
        else:
            return None

    def replace_content(self, template_content, file_content):
        contents = re.findall("<!-- pwb:content\('(.+)'\) -->", template_content)

        for content in contents:
            match = re.search("<!-- pwb:section\('"+content+"'\) -->\s*(.*?)\s*<!-- pwb:end-section -->", file_content, re.S)
            if match:
                template_content = re.sub("<!-- pwb:content\('" + content + "'\) -->", match.group(1), template_content)

        return template_content

website_builder = WebsiteBuilder()
website_builder.build()