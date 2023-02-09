from .utils import catch_keyboard_interrupt


@catch_keyboard_interrupt()
def cli():
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

    def print_success(text):
        print(f"\N{check mark} \033[32;1m{text}\033[0m")

    def print_warning(text):
        print(f"\N{warning sign} \033[33;1m{text}\033[0m")

    def print_error(error):
        print(f"\N{skull} \033[31;1m{error}\033[0m")
        exit()

    def parse_params(raw_params):
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

    def safe_chdir(dest):
        if not exists(dest):
            return
        chdir(dest)

    def abs_path(path, ext):
        return realpath(splitext(path)[0] + ext)

    def write_file(path, obj, ext, script_block):
        out = abs_path(path, ext)
        if not NO_CACHE:
            CACHED_OBJECTS[out] = obj
        if script_block not in SKIP_WRITE:
            if exists(out):
                remove(out)
            obj.write(out)

    def clean_path(file):
        path = realpath(file)
        if not exists(path):
            print_error(f"{path} does not exist.")
        return path

    def check_subdirectories(script):
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

    def define_directories(root):
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

    def create_new_template(template):
        chdir(ROOT_DIR)
        out_path = splitext(template)[0]
        name = basename(out_path)
        script = {
            "corpus": {
                "name": f"{name}-corpus",
                "source": [
                    join(AUDIO_DIR, "source.wav")
                ],
                "features": [
                    "timbre"
                ]
            },
            "mosaic": {
                "name": f"{name}-mosaic",
                "target": join(AUDIO_DIR, "target.wav"),
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

    parser = ArgumentParser(prog='GAMuT parser',
                            description="Command-line utility for creating GAMuT audio musaicings with JSON files",
                            epilog='To learn more, visit https://felipe-tovar-henao.com/gamut')
    parser.add_argument('-v', '--version',
                        action='store_true',
                        help='get current version of GAMuT')
    parser.add_argument('--test',
                        action='store_true',
                        help='runs GAMuT package test.')
    parser.add_argument('--no-check',
                        action='store_true',
                        help='Disable directory checking when reading a script')
    parser.add_argument('--no-cache',
                        action='store_true',
                        help='Disable pipeline caching')
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
    parser.add_argument('--skip',
                        nargs='+',
                        help="skip one or more parts of the script",
                        choices=SCRIPT_MODES)
    parser.add_argument('--skip-write',
                        nargs='+',
                        help="skip writing to disk one or more parts of the script",
                        choices=SCRIPT_MODES)
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
                        help="audio features to base audio musaicing on",
                        choices=['pitch', 'analysis'])
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

    # ------------------------------------- #
    # PRINT GAMUT PACKAGE VERSION
    # ------------------------------------- #
    if args.version:
        print_success(f'GAMuT v{pkg_resources.get_distribution("gamut").version}')

    # ------------------------------------- #
    # RUN PACKAGE TEST
    # ------------------------------------- #
    elif args.test:
        TEST_DIR = '.gamut-test'
        mkdir(TEST_DIR)
        TEST_DIR = realpath(TEST_DIR)
        try:
            safe_chdir(TEST_DIR)
            run(['gamut', '--init'])
            run(['gamut', '--script', join(basename(SCRIPTS_DIR), f"{TEST_NAME}.json"), '--no-cache'])
            print_success('GAMuT test successful!')
        except Exception as e:
            print(e)
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

        from .features import Corpus, Mosaic

        corpus = Corpus(**corpus_params)
        mosaic = Mosaic(target=target, corpus=corpus)
        audio = mosaic.to_audio(**params)
        if 'audio' not in SKIP_WRITE:
            write_file(args.audio, audio, ".wav", 'audio')
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
        filenames = ['source.wav', 'target.wav']

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

        print_success(
            f"Your GAMuT project folder is ready!\nTry running:\n\tgamut --script scripts/{TEST_NAME}.json --play")

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

        for script_block in script:
            if script_block not in SCRIPT_MODES:
                print_error(f'"{script_block}" is not a valid GAMuT script key')

        from .features import Corpus, Mosaic

        skip = args.skip if args.skip else []
        sorted_modes = [m for m in SCRIPT_MODES if m in script and m not in skip]

        for script_block in sorted_modes:
            params = script[script_block]
            name = params.pop('name', None)
            output_name = name if name else splitext(basename(script_path))[0] + f'-{script_block}'

            if script_block == 'corpus':
                safe_chdir(AUDIO_DIR)

                for i, source in enumerate(params['source']):
                    params['source'][i] = clean_path(source)
                safe_chdir(ROOT_DIR)
                c = Corpus(**params)
                safe_chdir(CORPUS_DIR)
                write_file(output_name, c, '.gamut', script_block)

            elif script_block == 'mosaic':
                for x in ['corpus', 'target']:
                    if x not in params:
                        print_error(f'You forgot to specify a {x} in your {script_block} script.')

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

            elif script_block == 'audio':
                mosaic_file = params.pop('mosaic')

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
                convolve = params.pop('convolve', None)
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
