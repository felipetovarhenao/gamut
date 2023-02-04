from argparse import ArgumentParser
from os.path import realpath, join, exists, dirname, splitext
from os import chdir, makedirs
import json
import importlib.util


def msg(text):
    print(f"\033[32;1m{text}\033[0m")


def throw(error):
    print(f"\033[31;1m{error}\033[0m")
    exit()


def new_template(template):
    with open(join(SCRIPTS_DIR, f'{template}.json'), 'w') as f:
        json.dump(TEMPLATES[template], f, indent=4)


# check package installation
if importlib.util.find_spec('gamut') == None:
    throw("You haven't installed the GAMuT package. You can find the installation guide here: https://felipe-tovar-henao.com/gamut/installation")

# ------------------------------------- #
# PARSE SCRIPT
# ------------------------------------- #


SCRIPT_MODES = ['corpus', 'mosaic', 'audio']

parser = ArgumentParser(
    prog='GAMuT parser', description="Project utility for creating GAMuT audio musaicings with JSON scripts",
    epilog='felipe-tovar-henao.com')
parser.add_argument('-i', '--init', action='store_true', help='Initializes a project folder structure')
parser.add_argument('-s', '--script', help="JSON file to use as input settings for GAMuT", type=str)
parser.add_argument('-p', '--play', action='store_true', help="Enable audio playback after script runs")
parser.add_argument(
    '-t', '--template', help=f"Generates a new script template, based on the following options: {SCRIPT_MODES}", type=str,
    choices=SCRIPT_MODES)
args = parser.parse_args()

# ------------------------------------- #
# FOLDER STRUCTURE
# ------------------------------------- #

ROOT_DIR = dirname(realpath(__file__))
chdir(ROOT_DIR)

GAMUT_DIR = join(ROOT_DIR, 'gamut')
MOSAIC_DIR = join(GAMUT_DIR, 'mosaics')
CORPUS_DIR = join(GAMUT_DIR, 'corpora')
AUDIO_DIR = join(ROOT_DIR, 'audio')
AUDIO_IN_DIR = join(AUDIO_DIR, 'input')
AUDIO_OUT_DIR = join(AUDIO_DIR, 'output')
SCRIPTS_DIR = join(ROOT_DIR, 'scripts')

TEMPLATES = {
    "corpus": {
        "corpus": {
            "name": "corpus-example",
            "params": {
                "source": [
                    join(AUDIO_IN_DIR, "source.wav")
                ],
                "features": [
                    "timbre",
                    "pitch"
                ]
            }
        }
    },
    "mosaic": {
        "mosaic": {
            "name": "mosaic-example",
            "params": {
                "target": join(AUDIO_IN_DIR, "target.wav"),
                "corpus": [
                    join(CORPUS_DIR, "corpus-example.gamut")
                ]
            }
        }
    },
    "audio": {
        "audio": {
            "name": "mosaic.wav",
            "params": {
                "mosaic": join(MOSAIC_DIR, "mosaic-example.gamut"),
                "fidelity": 1.0,
                "grain_dur": 0.1,
                "grain_env": "cosine",
                "corpus_weights": 1.0,
                "stretch_factor": 1.0,
                "pan_depth": 2,
                "n_chans": 2,
                "onset_var": 0,
            }
        }
    }
}

if args.init:

    for x in [GAMUT_DIR, MOSAIC_DIR, CORPUS_DIR, AUDIO_DIR, AUDIO_OUT_DIR, AUDIO_IN_DIR, SCRIPTS_DIR]:
        if not exists(x):
            makedirs(x)

    TEMPLATES['test'] = {k: TEMPLATES[k][k] for k in TEMPLATES}
    new_template('test')

    import requests
    import shutil

    base_url = 'https://d2cqospqxtt8fw.cloudfront.net/personal-website/gamut/'
    filenames = ['source.wav', 'target.wav']

    try:
        for f in filenames:
            with requests.get(base_url + f, stream=True) as r:
                with open(join(AUDIO_IN_DIR, f), 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
    except:
        print('\tWarning: Unable to download audio examples')

    msg('Your GAMuT project folder is ready!')
    exit()

if args.template:
    new_template(args.template)

if args.script:
    script_path = realpath(args.script)

    with open(file=script_path, mode='r',) as f:
        script = json.loads(f.read())

    # ------------------------------------- #
    # INITIAL SCRIPT VALIDATION
    # ------------------------------------- #

    for mode in script:
        if mode not in SCRIPT_MODES:
            throw(f'{mode} is not a valid GAMuT script key')

    from gamut.features import Corpus, Mosaic

    sorted_modes = [m for m in SCRIPT_MODES if m in script]
    for mode in sorted_modes:
        obj = script[mode]
        try:
            output_name = obj['name']
        except:
            throw(f'You forgot to specify a name for the {mode} output file')

        if 'params' not in obj:
            throw(f'You forgot to specify the {mode} "params" field in your script')

        # ------------------------------------- #
        # PROCESS GAMUT SCRIPT
        # ------------------------------------- #
        params = obj['params']
        if mode == 'corpus':
            chdir(AUDIO_DIR)
            for source in params['source']:
                params['source'] = realpath(source)
            chdir(ROOT_DIR)
            c = Corpus(**params)
            c.write(join(CORPUS_DIR, output_name))

        elif mode == 'mosaic':
            for x in ['corpus', 'target']:
                if x not in params:
                    throw(f'You forgot to specify a {x} in your {mode} script.')

            chdir(CORPUS_DIR)
            corpora = [Corpus().read(splitext(c)[0] + ".gamut") for c in params['corpus']]
            chdir(AUDIO_DIR)
            params['target'] = realpath(params['target'])
            chdir(ROOT_DIR)
            m = Mosaic(target=params['target'], corpus=corpora)
            m.write(join(MOSAIC_DIR, output_name))

        elif mode == 'audio':
            mosaic_file = params.pop('mosaic')
            chdir(MOSAIC_DIR)
            m = Mosaic().read(splitext(mosaic_file)[0] + ".gamut")
            chdir(ROOT_DIR)
            audio = m.to_audio(**params)
            audio.write(join(AUDIO_OUT_DIR, output_name))
            if args.play:
                audio.play()
