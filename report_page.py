import os
import argparse
import json

parser = argparse.ArgumentParser(prog='report_page.py', description='Create html report page for all scenes')

parser.add_argument('-directory', '-d', required=True)

args = parser.parse_args()

# node_name/gpu_name/backend_name/scene_name

def get_subdirectories(path):
    return [f for f in os.scandir(path) if f.is_dir()]

def get_trace_file(path):
    for entry in os.listdir(path):
        if entry.endswith('.pftrace'):
            return os.path.join(path, entry)
    return None

def normalize_webpath(path):
    webpath = ''
    if args.directory[len(args.directory) - 1] == '/':
        webpath = path.replace(args.directory, '')
    else:
        webpath = path.replace(args.directory + '/', '')

    return webpath


def get_render_file(path):
    for entry in os.listdir(path):
        if entry.startswith('render.'):
            webpath = normalize_webpath(path) 
            image_path = os.path.join(webpath, entry)
            return image_path
    return None

def read_float(path):
    with open(path, 'r') as file:
        return float(file.read().strip())

def get_file_content(file_path):
    file_content = ''
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content;

scenes = {}
nodes_info = []
#for node in get_subdirectories(os.path.abspath(args.directory)):
for node in get_subdirectories(args.directory):
    cpu = get_file_content(node.path + '/cpu_name')
    ram = float(get_file_content(node.path + '/avail_ram_in_kb').strip()) / 1024.0 / 1024.0
    info = { 
        'cpu': cpu, 
        'ram': ram,
        'gpus': []
    }
    for gpu in get_subdirectories(node):
        gpu_name = get_file_content(gpu.path + '/gpu_name')
        info['gpus'].append({
            'gpuName': gpu_name,
            'vram': 'unknown'
        })
        for backend in get_subdirectories(gpu):
            for scene in get_subdirectories(backend):
                if not scene.name in scenes:
                    scenes[scene.name] = []

                scene_data = {
                    'nodeName': node.name,
                    'backendName': backend.name,
                    'gpuName': gpu_name,
                    'imagePath': get_render_file(scene.path),
                    'renderTime': float(get_file_content(scene.path + '/render_time.txt').strip()),
                    'vramUsage': float(get_file_content(scene.path + '/vram_usage.txt').strip()),
                    'sceneDataPath' : normalize_webpath(scene.path),
                }

                trace_file = get_trace_file(scene.path)
                if not trace_file is None:
                    scene_data['perfettoTracePath'] = trace_file

                scenes[scene.name].append(scene_data)
    nodes_info.append(info)

with open('report_page_template.html', 'r') as report_page_template:
    content = report_page_template.read()
    report_page_input = json.dumps({ "scenes": scenes, "nodesInfo": nodes_info })
    content = content.replace('let pageInput = null;', 'let pageInput = ' + report_page_input + ';')
    with open(args.directory + '/index.html', 'w') as file:
        file.write(content)
