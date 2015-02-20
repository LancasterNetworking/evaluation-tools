import glob

def find_process_id(node_folder, name):
    folders = glob.glob(node_folder + '/var/log/*/cmdline')
    for folder in sorted(folders):
        with open(folder, 'r') as out:
            if name in [line for line in out.readlines()]:
                return folder.split('/')[-2]
    return None
