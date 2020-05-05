import os
import sys
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('command_name', help='commmand name to register', type=str, nargs='*', default='atjudge')
    args = parser.parse_args()

    targetfilepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'run.sh')
    # OSの判定
    if os.name == 'nt':
        cmd = [targetfilepath, 'C:/commands/' + args.command_name]
        # cmd = ['mklink',  + args.command_name, targetfilepath]
    elif os.name == 'posix':
        cmd = [targetfilepath, '/usr/local/bin/' + args.command_name]
    else:
        print('This OS is not supported\nPlease create a symbolic link or register an alias manually\n')
        print('ファイルパス：')
        print(targetfilepath)
        sys.exit()

    print('unlink path:' + ' '.join(cmd))

    try:
        os.symlink(*cmd)
    except FileExistsError as e:
        print(e)
    except OSError:
        print('Permission denied\nPlease run it again with administrative privileges')
    except Exception as e:
        print(e)
    else:
        print('The command was successfully registered.')
        print('We can run with "{}"'.format(args.command_name))