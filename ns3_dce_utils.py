import glob

def find_in_files(files, string):
    files = glob.glob(files)
    for f in sorted(files):
        with open(f, 'r') as out:
            for line in out.readlines():
                if string in line:
                    yield line, f

def find_process_id(node_folder, name):
    files = node_folder + '/var/log/*/cmdline'
    for line, f in find_in_files(files, name):
        return f.split('/')[-2]
    return None

"""
def find_process_id(node_folder, name):
    files = glob.glob(node_folder + '/var/log/*/cmdline')
    for f in sorted(files):
        with open(f, 'r') as out:
            for line in out.readlines():
                if name in line:
                    return f.split('/')[-2]
    return None
"""
