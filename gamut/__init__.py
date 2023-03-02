# typing
from collections.abc import Iterable

# gamut
from .utils import catch_keyboard_interrupt


def print_success(text) -> None:
    """ Prints green-colored message """
    print(f"\N{check mark} \033[32;1m{text}\033[0m")


def print_warning(text) -> None:
    """ Prints yellow-colored message """
    print(f"\N{warning sign} \033[33;1m{text}\033[0m")


def print_error(error) -> None:
    """ Prints red-colored message """
    print(f"\N{skull} \033[31;1m{error}\033[0m")
    exit()


def is_kivy_installed() -> bool:
    """ Check if kivy is installed """
    import pkg_resources
    return 'kivy' in list(map(lambda x: x.key, pkg_resources.working_set))


def gui() -> None:
    """ Entry points to launch GUI """
    # Check if kivy has been installed
    if not is_kivy_installed():
        import subprocess
        import threading
        from sys import executable

        # try installing on separate thread and wait until done
        print_warning("Attempting to install missing dependencies...")
        t = threading.Thread(target=lambda: subprocess.run([executable, '-m', 'pip', 'install', 'kivy[base]']))
        t.start()
        t.join()

        # run with --retry flag to prevent infinite recursion (see conditional in cli())
        print_success("Running again...")
        subprocess.run(['gamut', '--gui', '--retry'])
        exit()

    print_success('Launching user interface...')
    from .gui import GUI
    GUI().run()


@catch_keyboard_interrupt()
def cli():
    """ CLI entry point """
    from argparse import ArgumentParser
    from os import chdir, makedirs, remove, mkdir, getcwd
    from os.path import realpath, join, exists, splitext, basename
    from shutil import rmtree, copyfileobj
    import pkg_resources
    from subprocess import run
    from pathlib import Path
    import json
    import requests

    # ------------------------------------- #
    # HELPER FUNCTIONS
    # ------------------------------------- #

    def parse_params(raw_params: Iterable) -> dict:
        params = {}
        if not raw_params:
            return params
        for param in raw_params:
            key, value = param.split("=")
            try:
                value = float(value)
            except:
                pass
            if key in params:
                if not isinstance(params[key], list):
                    params[key] = [params[key]]
                params[key].append(value)
                continue
            params[key] = value
        return params

    def safe_chdir(dest: str) -> None:
        if not exists(dest):
            return
        chdir(dest)

    def abs_path(path: str, ext: str) -> str:
        return realpath(splitext(path)[0] + ext)

    def write_file(path: str, obj: object, ext: str, script_block: str) -> None:
        out = abs_path(path, ext)
        if not NO_CACHE:
            CACHED_OBJECTS[out] = obj
        if script_block not in SKIP_WRITE:
            if exists(out):
                remove(out)
            obj.write(out)

    def clean_path(file: str) -> str:
        path = realpath(file)
        if not exists(path):
            print_error(f"{path} does not exist.")
        return path

    def check_subdirectories(script: str) -> None:
        subdirs = [AUDIO_DIR, CORPUS_DIR, MOSAIC_DIR]
        missing = []
        for subdir in subdirs:
            if not exists(subdir):
                missing.append(basename(subdir))
        num_missing = len(missing)
        if num_missing == 0:
            return
        if num_missing > 0:
            for p in [Path(script).parent.parent.absolute(), Path(script).parent.absolute()]:
                found = True
                for subdir in subdirs:
                    if not exists(join(p, basename(subdir))):
                        found = False
                        break
                if found:
                    define_directories(p)
                    return
        if num_missing == len(subdirs):
            print_warning('You seem to be running this script from outside a workspace folder, which might result in unexpected behaviors.')
        elif num_missing > 0:
            print_warning(
                f'Your current directory is missing the following workspace folders:\n\t{", ".join(missing)}\nThis might result in unexpected behaviors.')
        answer = input("Would you like to continue (y/n)?")
        if answer.lower() in ['n', 'no']:
            exit()

    def define_directories(root: str) -> None:
        global ROOT_DIR
        global MOSAIC_DIR
        global CORPUS_DIR
        global AUDIO_DIR
        global SCRIPTS_DIR
        global TEST_NAME
        global TEST_SCRIPT_DIR
        ROOT_DIR = realpath(root)
        MOSAIC_DIR = join(ROOT_DIR, 'mosaics')
        CORPUS_DIR = join(ROOT_DIR, 'corpora')
        AUDIO_DIR = join(ROOT_DIR, 'audio')
        SCRIPTS_DIR = join(ROOT_DIR, 'scripts')
        TEST_NAME = 'test'
        TEST_SCRIPT_DIR = join(SCRIPTS_DIR, f'{TEST_NAME}.json')

    def create_new_template(template: str) -> None:
        chdir(ROOT_DIR)
        out_path = splitext(template)[0]
        name = basename(out_path)
        script = {
            "corpus": {
                "name": f"{name}-corpus",
                "source": [
                    join(AUDIO_DIR, DEFAULT_SOURCE)
                ],
                "features": [
                    "timbre"
                ]
            },
            "mosaic": {
                "name": f"{name}-mosaic",
                "target": join(AUDIO_DIR, DEFAULT_TARGET),
                "corpus": [
                    f"{name}-corpus"
                ]
            },
            "audio": {
                "name": f"{name}-audio",
                "mosaic": f"{name}-mosaic",
                "fidelity": 1.0,
                "grain_dur": 0.1,
                "grain_env": "cosine",
                "corpus_weights": 1.0,
                "stretch_factor": 1.0,
                "pan_depth": 3,
                "onset_var": 0.0,
                "n_chans": 2,
                "sr": 44100,
            }
        }
        with open(out_path + '.json', 'w') as f:
            json.dump(script, f, indent=4)

    # ------------------------------------- #
    # DEFINE FOLDER STRUCTURE
    # ------------------------------------- #
    define_directories(getcwd())

    # ------------------------------------- #
    # PARSE CLI ARGUMENTS
    # ------------------------------------- #
    CACHED_OBJECTS = {}
    SCRIPT_MODES = ['corpus', 'mosaic', 'audio']
    DEFAULT_SOURCE = 'source.mp3'
    DEFAULT_TARGET = 'target.mp3'

    parser = ArgumentParser(prog='GAMuT parser',
                            description="Command-line utility for creating GAMuT audio musaicings with JSON files",
                            epilog='To learn more, visit https://felipe-tovar-henao.com/gamut')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='get current version of GAMuT')
    parser.add_argument('--test',
                        action='store_true',
                        help='runs GAMuT package test.')
    parser.add_argument('--gui',
                        action='store_true',
                        help='open GAMuT graphical user interface.')
    parser.add_argument('--retry',
                        action='store_true',
                        help='Flag to signal attempt to re-run UI after kivy installation attempt.')
    parser.add_argument('--no-check',
                        action='store_true',
                        help='Disable directory checking when reading a script')
    parser.add_argument('--no-cache',
                        action='store_true',
                        help='Disable pipeline caching')
    parser.add_argument('--no-download',
                        action='store_true',
                        help='Disable audio when using --init')
    parser.add_argument('-i', '--init',
                        nargs='?',
                        const=ROOT_DIR,
                        help='initializes a project folder at the specified directory',
                        type=str)
    parser.add_argument('-s', '--script',
                        help="set JSON file to use as input settings for GAMuT",
                        type=str)
    parser.add_argument('--summarize',
                        help="show summary of a .gamut file",
                        type=str)
    parser.add_argument('-p', '--play',
                        action='store_true',
                        help="enable audio playback after script runs")
    parser.add_argument('--no-verbose',
                        action='store_true',
                        help="disables console printing")
    parser.add_argument('--skip',
                        nargs='+',
                        help="skip one or more blocks from the script")
    parser.add_argument('--skip-write',
                        nargs='+',
                        help="skip writing to disk one or more blocks from the script")
    parser.add_argument('-t', '--template',
                        nargs='?',
                        const=TEST_SCRIPT_DIR,
                        help="generate a JSON script template",
                        type=str)
    parser.add_argument('--source',
                        nargs='+',
                        help="path to corpus source(s)")
    parser.add_argument('--params',
                        nargs='+',
                        help="audio control parameters")
    parser.add_argument('--features',
                        nargs='+',
                        help="audio features to base audio musaicking on",
                        choices=['pitch', 'timbre'])
    parser.add_argument('--target',
                        help="path to audio target",
                        type=str)
    parser.add_argument('--audio',
                        default="gamut-output.wav",
                        help='path to audio output',
                        type=str)

    args = parser.parse_args()

    NO_CACHE = args.no_cache
    SKIP_WRITE = args.skip_write or []
    raw_musaicing_args = [args.source, args.target]

    if len(SKIP_WRITE) > 0 and NO_CACHE:
        print_error("You can't use --skip-write and --no-cache at the same time.")

    if args.no_verbose:
        from .sys import set_vebosity
        set_vebosity(False)

    # ------------------------------------- #
    # PRINT GAMUT PACKAGE VERSION
    # ------------------------------------- #
    if args.version:
        print_success(f'GAMuT v{pkg_resources.get_distribution("gamut").version}')

    # ------------------------------------- #
    # OPEN GRAPHICAL USER INTERFACE
    # ------------------------------------- #
    elif args.gui:
        if not is_kivy_installed() and args.retry:
            print('Unable to install kivy library. Please visit https://kivy.org/doc/stable/gettingstarted/installation.html#install-pip to install it manually and try again afterwards.')
        import subprocess
        subprocess.run(['gamut-ui'])

    # ------------------------------------- #
    # RUN PACKAGE TEST
    # ------------------------------------- #
    elif args.test:
        TEST_DIR = realpath('.gamut-test')
        if exists(TEST_DIR):
            rmtree(TEST_DIR)
        mkdir(TEST_DIR)
        safe_chdir(TEST_DIR)
        print_success("Running test...")
        run(['gamut', '--init', '--no-verbose'])
        run(['gamut', '--script', join(basename(SCRIPTS_DIR), f"{TEST_NAME}.json"), '--no-cache', '--no-verbose'])
        print_success("Done")
        rmtree(TEST_DIR)

    # ------------------------------------- #
    # PROCESS RAW INPUT
    # ------------------------------------- #
    elif any(raw_musaicing_args):
        if not all(raw_musaicing_args):
            print_error("You must provide both source and target")
        params = parse_params(args.params)
        source, target = raw_musaicing_args
        target = clean_path(target)
        corpus_params = {
            'source': [clean_path(s) for s in source]
        }
        if args.features:
            corpus_params['features'] = args.features

        impulse_response = params.pop('impulse_response', None)
        if impulse_response:
            convolve_params = {
                'impulse_response': clean_path(impulse_response)
            }
            convolve_mix = params.pop('convolve_mix', None)
            if convolve_mix:
                convolve_params['mix'] = convolve_mix

        from .features import Corpus, Mosaic

        corpus = Corpus(**corpus_params)
        mosaic = Mosaic(target=target, corpus=corpus)
        audio = mosaic.to_audio(**params)
        write_file(args.audio, audio, '.wav', 'audio')
        if impulse_response:
            audio.convolve(**convolve_params)
        if args.play:
            audio.play()

    # ------------------------------------- #
    # INITIALIZE WORKSPACE
    # ------------------------------------- #
    elif args.init:
        if realpath(args.init) != ROOT_DIR:
            define_directories(args.init)
        for x in [MOSAIC_DIR, CORPUS_DIR, AUDIO_DIR, SCRIPTS_DIR]:
            if not exists(x):
                makedirs(x)
        create_new_template(TEST_SCRIPT_DIR)

        base_url = 'https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/'
        filenames = [DEFAULT_SOURCE, DEFAULT_TARGET]

        if not args.no_download:
            try:
                for f in filenames:
                    file_path = join(AUDIO_DIR, f)
                    if exists(file_path):
                        continue
                    with requests.get(base_url + f, stream=True) as r:
                        with open(file_path, 'wb') as f:
                            copyfileobj(r.raw, f)
            except:
                print('\tWarning: Unable to download audio examples')
        if not args.no_verbose:
            print_success(f"Your GAMuT project folder is ready! Try running:\n\tgamut --script scripts/{TEST_NAME}.json --play")

    # ------------------------------------- #
    # CREATE TEMPLATE
    # ------------------------------------- #

    elif args.template:
        safe_chdir(SCRIPTS_DIR)
        create_new_template(args.template)

    # ------------------------------------- #
    # SUMMARIZE GAMUT FILE
    # ------------------------------------- #

    elif args.summarize:
        gamut_file = args.summarize
        if not exists(gamut_file):
            print_error(f'{gamut_file} does not exist.')

        if splitext(gamut_file)[1] != '.gamut':
            print_error(f'{gamut_file} is not a .gamut file')

        from .features import Corpus, Mosaic

        for obj in [Corpus(), Mosaic()]:
            try:
                obj.read(gamut_file).summarize()
            except:
                continue
            break

    # ------------------------------------- #
    # PROCESS SCRIPT
    # ------------------------------------- #

    elif args.script:
        script_path = clean_path(args.script)

        if not args.no_check:
            check_subdirectories(script_path)

        with open(file=script_path, mode='r',) as f:
            script = json.loads(f.read())

        # validate skipped blocks and warn if they don't exist
        skipped_blocks = args.skip if args.skip else []
        for skip_list in [skipped_blocks, SKIP_WRITE]:
            for skipped in skip_list:
                if skipped not in script:
                    print_warning(f"trying to skip a block that isn't included in the script: \"{skipped}\". ignoring...")

        # create mapping of script blocks to their types
        block_type_map = {}
        for script_block in script:
            fail = True
            for sm in SCRIPT_MODES:
                if script_block.startswith(sm):
                    fail = False
                    if script_block not in skipped_blocks:
                        block_type_map[script_block] = sm
                    break
            if fail:
                print_error(
                    f'"{script_block}" is not a valid GAMuT script block. It should start with one of the following: {SCRIPT_MODES}')

        from .features import Corpus, Mosaic

        # process each block
        for script_block in block_type_map:
            params = script[script_block]
            block_type = block_type_map[script_block]

            name = params.pop('name', None)
            output_name = name if name else splitext(basename(script_path))[0] + f'-{script_block}'

            if block_type == 'corpus':
                safe_chdir(AUDIO_DIR)
                for i, source in enumerate(params['source']):
                    params['source'][i] = clean_path(source)
                safe_chdir(ROOT_DIR)
                c = Corpus(**params)
                safe_chdir(CORPUS_DIR)
                write_file(output_name, c, '.gamut', script_block)

            elif block_type == 'mosaic':
                for x in ['corpus', 'target']:
                    if x not in params:
                        print_error(f'You forgot to specify a {x} in your {block_type} script.')

                # clean target path
                safe_chdir(AUDIO_DIR)
                params['target'] = clean_path(params['target'])

                # clean beat unit
                if 'beat_unit' in params:
                    try:
                        if "/" in params['beat_unit']:
                            a, b = params['beat_unit'].split('/')
                            params['beat_unit'] = int(a) / int(b)
                        else:
                            params['beat_unit'] = int(params['beat_unit'])
                    except:
                        print_error('Invalid "beat_unit" value')

                # clean corpus paths
                safe_chdir(CORPUS_DIR)
                corpus_paths = params.pop('corpus')
                corpora = []
                for c in corpus_paths:
                    cpath = abs_path(c, '.gamut')
                    if cpath in CACHED_OBJECTS:
                        corpora.append(CACHED_OBJECTS[cpath])
                        continue
                    cpath = clean_path(cpath)
                    corpora.append(Corpus().read(cpath))

                # build mosaic
                safe_chdir(ROOT_DIR)
                m = Mosaic(corpus=corpora, **params)

                # write to disk
                safe_chdir(MOSAIC_DIR)
                write_file(output_name, m, '.gamut', script_block)

            elif block_type == 'audio':
                mosaic_file = params.pop('mosaic')
                convolve = params.pop('convolve', None)

                # clean mosaic path
                safe_chdir(MOSAIC_DIR)
                mosaic_path = abs_path(mosaic_file, '.gamut')
                m = Mosaic().read(clean_path(mosaic_path)
                                  ) if mosaic_path not in CACHED_OBJECTS else CACHED_OBJECTS[mosaic_path]

                # create audio mosaic
                safe_chdir(ROOT_DIR)
                audio = m.to_audio(**params)
                safe_chdir(AUDIO_DIR)

                # clean convolution
                if convolve:
                    if 'impulse_response' not in convolve:
                        print_error('To apply audio convolution, you must provide an inpulse response')
                    convolve['impulse_response'] = clean_path(convolve['impulse_response'])
                    audio.convolve(**convolve)
                write_file(output_name, audio, '.wav', script_block)
                if args.play:
                    audio.play()
    else:
        print_error("You didn't provide any required arguments. Use -h or --help to learn more.")
