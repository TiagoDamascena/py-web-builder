import json
import os
import shutil
import re
import markdown2

config = json.load(open('builder.json', 'r'))
destination_folder = config['config']['build_folder']

def copy_files(copy_from, copy_to):
    if os.path.isdir(copy_from):
        shutil.copytree(copy_from, destination_folder + copy_to)
    else:
        shutil.copy(copy_from, destination_folder + copy_to)

def build_files(current_content, current_path, content=None):
    if os.path.isdir(current_path):
        paths = os.listdir(current_path)
        for path in paths:
            build_files(current_content, os.path.join(current_path, path), content)
    else:
        file_content = open(current_path, 'r').read()

        file_format = os.path.splitext(current_path)[1]

        if current_content:
            replace = re.findall(r'{{(\w+)}}', current_content)
            for tag in replace:
                text = re.search(r'{{'+tag+'}}(.*){{'+tag+'}}', file_content, re.S)
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
            result_path = destination_folder + os.path.splitext(current_path)[0] + '.html'
            if not os.path.exists(os.path.dirname(result_path)):
                os.makedirs(os.path.dirname(result_path))

            result = open(result_path, 'w')
            result.write(current_content)
            result.close()

# Destroy old destination folder
shutil.rmtree(destination_folder)

# Copy selected files
copy_config = config['copy']
print 'Copying files...'
for copy in copy_config:
    copy_files(copy['from'], copy['to'])
print 'Files copied successfully!'

# Build pages from templates
build_config = config['build']
print 'Building files...'
for build in build_config:
    build_files('', build['path'], build['content'])
print 'Files builded successfully!'