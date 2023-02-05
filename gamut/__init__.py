def msg(text):
    print(f"\N{check mark} \033[32;1m{text}\033[0m")


def throw(error):
    print(f"\N{skull} \033[31;1m{error}\033[0m")
    exit()


def cli():
    from argparse import ArgumentParser
    from shutil import copyfile, rmtree
    from os import getcwd, mkdir, chdir
    from os.path import join, dirname, exists, realpath
    from sys import executable
    from subprocess import run
    import pkg_resources

    CWD = getcwd()
    PARSER_FILENAME = 'parser.py'

    parser = ArgumentParser(prog='GAMuT: Granular Audio Musiacing Toolkit',
                            description='Command-line utility for the GAMuT package',
                            epilog='To learn more, visit https://felipe-tovar-henao.com/gamut')
    parser.add_argument('--start', nargs='?', const=CWD, help='initializes a project folder at the specified directory', type=str)
    parser.add_argument('--phelp', action='store_true', help='read parser.py help reference.')
    parser.add_argument('--test', action='store_true', help='run package test.')
    parser.add_argument('-v', '--version', action='store_true', help='get current version')
    args, rest = parser.parse_known_args()

    def copy_parser(dir):
        copyfile(join(dirname(__file__), PARSER_FILENAME), join(dir, PARSER_FILENAME))

    def check_parser():
        if not exists(PARSER_FILENAME):
            throw(f"You seem to be trying to the GAMuT parser, but this directory does not contain a parser.py file.\nNavigate to a pre-existent project folder, or run 'gamut --start' to initialize a new one in this directory.")

    if args.version:
        msg(f'GAMuT v{pkg_resources.get_distribution("gamut").version}')
        exit()
    elif args.start:
        workspace = (args.start)
        if not exists(workspace):
            mkdir(workspace)
        workspace = realpath(workspace)
        copy_parser(workspace)
        chdir(workspace)
        run([executable, PARSER_FILENAME, '--init'])
        exit()
    elif args.test:
        TEST_DIR = '.gamut-test'
        mkdir(TEST_DIR)
        TEST_DIR = realpath(TEST_DIR)
        try:
            chdir(TEST_DIR)
            copy_parser(TEST_DIR)
            run([executable, PARSER_FILENAME, '--init'])
            run([executable, PARSER_FILENAME, '--script', 'scripts/test.json'])
            msg('GAMuT test successful!')
        except Exception as e:
            print(e)
        rmtree(TEST_DIR)
        exit()
    elif args.phelp:
        check_parser()
        run([executable, PARSER_FILENAME, '--help'])
        exit()
    elif rest:
        check_parser()
        run([executable, PARSER_FILENAME, *rest])
        exit()
    throw(f"You must provide at least one argument. Run 'gamut --help' to learn more.")
