if __name__ != '__main__':
    exit()

from argparse import ArgumentParser
from os.path import realpath, join, exists, dirname, splitext, basename
from os import chdir, makedirs, remove
import json
import importlib.util


# ------------------------------------- #
# HELPER FUNCTIONS
# ------------------------------------- #

def msg(text):
    print(f"\N{check mark} \033[32;1m{text}\033[0m")


def throw(error):
    print(f"\N{skull} \033[31;1m{error}\033[0m")
    exit()


def write_file(path, obj, ext):
    out = splitext(path)[0] + ext
    if exists(out):
        remove(out)
    obj.write(out)


def new_template(template):
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
            "onset_var": 0,
            "n_chans": 2,
            "sr": 44100,
        }
    }
    with open(out_path + '.json', 'w') as f:
        json.dump(script, f, indent=4)


# ------------------------------------- #
# CHECK PACKAGE INSTALLATION
# ------------------------------------- #

if importlib.util.find_spec('gamut') == None:
    throw("You haven't installed the GAMuT package. You can find the installation guide here: https://felipe-tovar-henao.com/gamut/installation")

# ------------------------------------- #
# DEFINE FOLDER STRUCTURE
# ------------------------------------- #

ROOT_DIR = dirname(realpath(__file__))
chdir(ROOT_DIR)

MOSAIC_DIR = join(ROOT_DIR, 'mosaics')
CORPUS_DIR = join(ROOT_DIR, 'corpora')
AUDIO_DIR = join(ROOT_DIR, 'audio')
SCRIPTS_DIR = join(ROOT_DIR, 'scripts')
SCRIPTS_CORPUS_DIR = join(SCRIPTS_DIR, 'corpora')
SCRIPTS_MOSAIC_DIR = join(SCRIPTS_DIR, 'mosaics')
SCRIPTS_AUDIO_DIR = join(SCRIPTS_DIR, 'audio')

# ------------------------------------- #
# PARSE CLI ARGUMENTS
# ------------------------------------- #

SCRIPT_MODES = ['corpus', 'mosaic', 'audio']
TEST_NAME = 'test'
TEST_SCRIPT_DIR = join(SCRIPTS_DIR, f'{TEST_NAME}.json')
TEMPLATE_OPTIONS = SCRIPT_MODES + [TEST_NAME]

parser = ArgumentParser(
    prog='GAMuT parser', description="Command-line utility for creating GAMuT audio musaicings with JSON files",
    epilog='To learn more, visit https://felipe-tovar-henao.com/gamut')
parser.add_argument('-i', '--init', action='store_true', help='initialize a workspace folder')
parser.add_argument('-s', '--script', help="set JSON file to use as input settings for GAMuT", type=str)
parser.add_argument('--summarize', help="show summary of a .gamut file", type=str)
parser.add_argument('-p', '--play', action='store_true', help="enable audio playback after script runs")
parser.add_argument('--skip', nargs='+', help="skip one or more parts of the script", choices=SCRIPT_MODES)
parser.add_argument('-t', '--template', nargs='?', const=TEST_SCRIPT_DIR, help="generate a JSON script template", type=str)
args = parser.parse_args()

# ------------------------------------- #
# INIT FLAG
# ------------------------------------- #


if args.init:
    for x in [MOSAIC_DIR, CORPUS_DIR, AUDIO_DIR, SCRIPTS_DIR]:
        if not exists(x):
            makedirs(x)
    new_template(TEST_SCRIPT_DIR)

    import requests
    import shutil

    base_url = 'https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/'
    filenames = ['source.wav', 'target.wav']

    try:
        for f in filenames:
            with requests.get(base_url + f, stream=True) as r:
                with open(join(AUDIO_DIR, f), 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
    except:
        print('\tWarning: Unable to download audio examples')

    msg('Your GAMuT project folder is ready!')
    exit()


# ------------------------------------- #
# CREATE TEMPLATE
# ------------------------------------- #

elif args.template:
    chdir(SCRIPTS_DIR)
    new_template(args.template)
    exit()

# ------------------------------------- #
# SUMMARIZE GAMUT FILE
# ------------------------------------- #

elif args.summarize:
    gamut_file = args.summarize
    if not exists(gamut_file):
        throw(f'{gamut_file} does not exist.')

    if splitext(gamut_file)[1] != '.gamut':
        throw(f'{gamut_file} is not a .gamut file')

    from gamut.features import Corpus, Mosaic
    for obj in [Corpus(), Mosaic()]:
        try:
            obj.read(gamut_file).summarize()
        except:
            continue
        exit()

# ------------------------------------- #
# PROCESS SCRIPT
# ------------------------------------- #

elif args.script:
    script_path = realpath(args.script)

    with open(file=script_path, mode='r',) as f:
        script = json.loads(f.read())

    for mode in script:
        if mode not in SCRIPT_MODES:
            throw(f'"{mode}" is not a valid GAMuT script key')

    from gamut.features import Corpus, Mosaic

    skip = args.skip if args.skip else []
    sorted_modes = [m for m in SCRIPT_MODES if m in script and m not in skip]
    for mode in sorted_modes:
        params = script[mode]
        name = params.pop('name', None)
        output_name = name if name else splitext(basename(script_path))[0] + f'-{mode}'

        match mode:
            case 'corpus':
                chdir(AUDIO_DIR)
                for source in params['source']:
                    params['source'] = realpath(source)
                chdir(ROOT_DIR)
                c = Corpus(**params)
                chdir(CORPUS_DIR)
                write_file(output_name, c, '.gamut')

            case 'mosaic':
                for x in ['corpus', 'target']:
                    if x not in params:
                        throw(f'You forgot to specify a {x} in your {mode} script.')

                chdir(CORPUS_DIR)
                corpora = [Corpus().read(splitext(c)[0] + ".gamut") for c in params['corpus']]
                chdir(AUDIO_DIR)
                params['target'] = realpath(params['target'])
                chdir(ROOT_DIR)
                m = Mosaic(target=params['target'], corpus=corpora)
                chdir(MOSAIC_DIR)
                write_file(output_name, m, '.gamut')

            case 'audio':
                mosaic_file = params.pop('mosaic')
                play = params.pop('play', None)
                convolve = params.pop('convolve', None)
                if convolve:
                    if 'impulse_response' not in convolve:
                        throw('To apply audio convolution, you must provide an inpulse response')
                    elif not exists(convolve['impulse_response']):
                        throw('Invalid impulse response path in convolve parameter')
                chdir(MOSAIC_DIR)
                m = Mosaic().read(splitext(mosaic_file)[0] + ".gamut")
                chdir(ROOT_DIR)
                audio = m.to_audio(**params)
                chdir(AUDIO_DIR)
                if convolve:
                    audio.convolve(**convolve)
                write_file(output_name, audio, '.wav')
                if args.play or play:
                    audio.play()
    exit()
else:
    throw("You didn't provide any arguments. Use -h or --help to learn more.")
