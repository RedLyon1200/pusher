#!/usr/bin/env python3

import sys
import os
import subprocess
import json


class Pusher:
    settings_path = os.path.abspath(__file__)
    settings_path = settings_path.replace('pusher.py', 'settings.json')

    def __init__(self):
        """Save or load settings in a json file"""
        opt = ' '

        if os.path.exists(self.settings_path):
            with open(self.settings_path) as f_obj:
                info = json.load(f_obj)

                self.tasker = info['tasker']
                self.commit = info['commit']
        else:
            msg.message('Settings:')
            config = {}

            while opt not in 'nNyY':
                opt = input(
                    '¿Desea utulizar el tasker para los commits por defecto?: Y/n\n')

            if opt in 'yY':
                config['tasker'] = True
            else:
                config['tasker'] = False

            print(
                '\nIngrese [#] si desea que su commit tenga el nombre del archivo\n\n\tEjemplo: archivo [#] subido == archivo pusher.py subido\n')
            config['commit'] = input('Inserte su commit por defecto: ')

            self.tasker = config['tasker']
            self.commit = config['commit']

            with open(self.settings_path, 'w') as f_obj:
                json.dump(config, f_obj, indent=4)

    def list_mod(self, files):
        """Modified files are captured"""
        try:
            return str(subprocess.check_output(
                "git status -s {} | grep ' M '".format(files), shell=True)).replace("b'", '').replace(
                ' M ', '').replace("\\n", "\n").replace("'", '').strip().split()
        except Exception:
            msg.warning(
                'There are no modified files that need to be uploaded')
            exit(1)

    def list_new(self, files):
        """New files are captured"""
        try:
            return str(subprocess.check_output(
                "git status -s {} | grep '?? '".format(files), shell=True)).replace("b'", '').replace(
                '?? ', '').replace("\\n", "\n").replace("'", '').strip().split()
        except Exception:
            msg.warning('There are no new files that need to be uploaded')
            exit(1)

    def list_all(self, files):
        """All files are captured"""
        try:
            return str(subprocess.check_output(
                "git status -s {}".format(files), shell=True)).replace("b'", '').replace(
                '?? ', '').replace(' M ', '').replace("\\n", "\n").replace("'", '').replace(' D ', '') .strip().split()

        except Exception:
            msg.warning('There are no files that need to be uploaded')
            exit(1)


class Msg:
    """colors"""
    BLUE = '\033[94m'
    GREEN = '\033[92m'

    """settings"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    """custom msg types"""
    OK = '\n\033[92m☑ Pusher:\033[0m '
    WARNING = '\n\033[93m⚠ Pusher:\033[0m '
    FAIL = '\n\033[91m⛔ Pusher:\033[0m '

    def error(self, message):
        """[Error message]"""
        print(self.FAIL + message + '\n')

    def message(self, msg):
        """[General message]"""
        print(msg + '\n')

    def warning(self, message):
        """[Warning message]"""
        print(self.WARNING + message + '\n')

    def ok(self, message):
        """[Ok message]"""
        print(self.OK + message + '\n')


def get_files():

    count = len(sys.argv[1:])
    usage = Msg.BLUE + \
        '\nUsage: pusher <option> [files]\n\nOptions:\n    -m (modified)\n    -n (new)\n    -a (all)\n'

    if count is 0:
        print(usage)
        exit(1)

    option = sys.argv[1]
    files = ['.']
    if count > 1:
        files = sys.argv[2:]
    files = " ".join(files).strip()

    if option == '-m':
        return pusher.list_mod(files)
    elif option == '-n':
        return pusher.list_new(files)
    elif option == '-a':
        return pusher.list_all(files)
    else:
        print(usage)
        exit(1)


def push(custom=False):
    """push inmediatly or not"""
    opt = ' '
    commit = 'custom' if custom else 'default'

    branch = str(subprocess.check_output("git branch", shell=True))

    for x, y in enumerate(branch):
        if y == '*':
            start = x + 2
            for i, j in enumerate(branch[start:]):
                if j == '\\':
                    end = start + i
                    break

    branch = branch[start:end]

    while opt not in ['Y', 'y', 'N', 'n']:
        opt = input(Msg.BLUE + '\n\n⍰ ' + Msg.RESET +
                    'You want to upload the files now? [Y/n]\n-> ')
    if opt in 'yY':
        print(Msg.GREEN + '\nUploading files...\033[0m')
        os.system('git push -u origin {}'.format(branch))
        msg.ok('Files uploaded with {} commit to {} branch.\n'.format(
            commit, branch))
    else:
        msg.warning('use "git push" to publish your local commits')


def add(file, commit):
    os.system('git add {}'.format(file))
    print('\nFile: {}'.format(file))
    os.system("git commit -m '{}'".format(commit))


if __name__ == "__main__":
    msg = Msg()
    pusher = Pusher()
    files = get_files()

    if len(files) == 0:
        msg.error('There are no files that need to be uploaded')
        exit(1)

    if pusher.tasker:
        if os.path.isfile('.tasks'):
            with open('.tasks') as f_obj:
                tasks = f_obj.read().replace("'", "´").splitlines()
                for itemname in files:
                    print(f"%%%%%%%%%", itemname)

                    for task in tasks:
                        commit_flag = False
                        """ print(f"###########", task) """
                        if task.find('./' + itemname) >= 0:
                            commit = task.replace('./' + itemname, '')
                            add(itemname, commit)
                            commit_flag = True
                            break

                    if commit_flag == False:
                        print('nombre de archivo no encontrado en .tasks')
                        commit = input('Inserte commit: ')
                        add(itemname, commit)
                push()

        else:
            msg.error(
                'You must first run the command:\ntasker <intranet_project_url>')
            exit(1)
    else:
        changecommit = input(
            Msg.BLUE + '\nHow do you want to handle commits?\n0 - Default\n1 - Edit\nOpt: ' + Msg.RESET)

        if changecommit not in '01':
            msg.error('Invalid option ' + changecommit)
            exit(1)

        if changecommit == '0':
            for itemname in files:
                commit = pusher.commit
                commit = commit.replace('[#]', itemname)
                add(itemname, commit)
            push()

        else:
            for itemname in files:
                commit = input(
                    msg.BLUE + '\nFile: \033[0m{}\n\033[94mInsert commit: \033[0m'.format(itemname))
                commit = commit.replace('[#]', itemname)
                add(itemname, commit)
            push(custom=True)
