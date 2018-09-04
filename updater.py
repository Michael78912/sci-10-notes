from urllib.request import urlopen
import sys
import os
import shutil
import colorama
import collections
import zipfile

# initiate colorama if on windows
if os.name == 'nt':
    colorama.init()

def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for i in zf.namelist():
            zf.extract(i, dest_dir)

# temporary directory for archive placement
TMP = os.environ['TMP'] if os.name == 'nt' else '/tmp'
# home directory == UserProfile on windows
HOME = os.environ['UserProfile' if os.name == 'nt' else 'HOME'] 

# check if program is frozen or not. __file__ does not
# exist if it is frzoen
FROZEN = getattr(sys, 'frozen', False)
FILE = sys.executable if FROZEN else __file__

# get the current version
with open(os.path.join(os.path.dirname(FILE), 'VERSION')) as F:
    CURRENT = F.read().strip()

# get the (possibly) updated version
with urlopen('https://raw.githubusercontent.com/Michael78912/sci-10-notes/master/VERSION') as F:
    NEXT = F.read().decode().strip()

def main():
    # set foreground colour to green
    sys.stdout.write(colorama.Fore.GREEN)
    
    print('version %s is available. update? (y/n): ' % NEXT, end='')
    choice = input().lower()
    # choice must be y or n
    while choice not in 'yn':
        sys.stdout.write(colorama.Fore.RED)
        choice = input('invalid choice. (y/n): ').lower()
        sys.stdout.write(colorama.Fore.GREEN)
        if choice == 'n':
            # simply exit if choice is no
            sys.stdout.write(colorama.Style.RESET_ALL)
            sys.exit()
        elif choice == 'y':
            # exit the loop
            sys.stdout.write(colorama.Fore.GREEN)
            break

    update()

def posix_opt(path):
    cho = input('open terminal in installed directory? (type y for yes): ').lower() == 'y'
    # replace current process with shell and reset colours
    sys.stdout.write(colorama.Style.RESET_ALL)
    if cho:
        os.execl(os.environ['SHELL'], os.environ['SHELL'],
                 '-c', "cd {} && {}".format(path, os.environ['SHELL']))

def nt_opt(path):
    cho = input('open explorer in installed directory? (type y for yes): ').lower() == 'y'
    sys.stdout.write(colorama.Style.RESET_ALL)
    if cho:
        os.execlp('explorer.exe', 'explorer', path)
    
    
# this function is mandatory because
# shutil.copytree requires the directory not
# to exist
def copytree(src, dest):
    for i in os.listdir(src):
        s = os.path.join(src, i)
        d = os.path.join(dest, i)
        if os.path.isdir(s):
            shutil.copytree(s, d)
        else:
            shutil.copyfile(s, d)
        
def update():
    # remove previous installation
    # copy the online version of branch master
    # to the temporary directory
    with urlopen('https://github.com/Michael78912/sci-10-notes/archive/master.zip') as new, \
            open(os.path.join(TMP, 'sci-10-notes.zip'), 'wb') as arc:
                shutil.copyfileobj(new, arc)

    # extract the archive to TMP directory.
    # the directory in tmp will be sci10notes-master. this
    # will be copied to home.
    unzip(os.path.join(TMP, 'sci-10-notes.zip'), TMP)

    # check if a release notes file exists. if it does, then display it.
    sys.stdout.write(colorama.Fore.CYAN)
    if os.path.exists(os.path.join(TMP, 'sci-10-notes-master', 'RELEASE')):
        print('*****Release Notes*****\n\n', open(
            os.path.join(TMP, 'sci10notes-master', 'RELEASE')).read())
    else:
        print(colorama.Fore.YELLOW, 'No release notes', colorama.Fore.GREEN)

    desktop_dir = os.path.join(HOME, 'Desktop')

    # optionally get an installation directory
    print('install to where? default is desktop: ({})'.format(desktop_dir), end='')
    path = os.path.join((input() or desktop_dir), 'Notes')

    if not os.path.isdir(path):
        sys.stdout.write(colorama.Fore.RED)
        print('Fatal: directory does not exist!')
        sys.stdout.write(colorama.Style.RESET_ALL)
        sys.exit()

    # copy files
    src = os.path.join(TMP, 'sci-10-notes-master', 'Notes')
    try:
        # remove previous install
        print(path)
        shutil.rmtree(path)
    except FileNotFoundError:
        pass
    copytree(src, path)
    print("copying updater ({})".format(FILE))
    shutil.copy(FILE, 'Notes')
    print('installed successfully! :) YAY')

    print('checking if this installation is a different place...')
    if os.path.dirname(FILE) != path:
        print(colorama.Fore.YELLOW, 'It is... removing this installation...',
              colorama.Fore.GREEN)
        shutil.rmtree(os.path.dirname(FILE))
    else:
        print('Same location, all good.')
    
    # call a proper option function based on the platform
    {
        'posix': posix_opt,
        'nt': nt_opt,
    }[os.name](path)        
 


if __name__ == '__main__':
    if NEXT != CURRENT: main()
    else: posix_opt() if os.name == 'posix' else nt_opt()


    
