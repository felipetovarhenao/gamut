if __name__ != '__main__':
    exit()

from argparse import ArgumentParser
from os.path import realpath, join, exists, dirname, splitext, basename
from os import chdir, makedirs
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


def new_template(template):
    dirs = {m: d for (m, d) in zip(TEMPLATE_OPTIONS, [SCRIPTS_CORPUS_DIR,
                                                      SCRIPTS_MOSAIC_DIR, SCRIPTS_AUDIO_DIR, SCRIPTS_DIR])}
    try:
        out_dir = dirs[template]
    except:
        throw(f"Invalid template type. Options are: {TEMPLATE_OPTIONS}")

    if not exists(out_dir):
        makedirs(out_dir)

    with open(join(out_dir, f'{template}.json'), 'w') as f:
        json.dump(TEMPLATES[template], f, indent=4)


# ------------------------------------- #
# CHECK PACKAGE INSTALLATION
# ------------------------------------- #

if importlib.util.find_spec('gamut') == None:
    throw("You haven't installed the GAMuT package. You can find the installation guide here: https://felipe-tovar-henao.com/gamut/installation")

# ------------------------------------- #
# PARSE CLI ARGUMENTS
# ------------------------------------- #


SCRIPT_MODES = ['corpus', 'mosaic', 'audio']
TEST_NAME = 'test'
TEMPLATE_OPTIONS = SCRIPT_MODES + [TEST_NAME]

parser = ArgumentParser(
    prog='GAMuT parser', description="Project utility for creating GAMuT audio musaicings with JSON scripts",
    epilog='To learn more, visit https://felipe-tovar-henao.com/gamut')
parser.add_argument('-i', '--init', action='store_true', help='initializes a project folder structure')
parser.add_argument('-s', '--script', help="JSON file to use as input settings for GAMuT", type=str)
parser.add_argument('-p', '--play', action='store_true', help="Enable audio playback after script runs")
parser.add_argument('--skip', nargs='+', help="Skip one or more parts of the script", choices=SCRIPT_MODES)
parser.add_argument(
    '-t', '--template', help=f"Generates a new script template, based on the following options: {TEMPLATE_OPTIONS}",
    type=str, choices=TEMPLATE_OPTIONS)
args = parser.parse_args()

# ------------------------------------- #
# DEFINE FOLDER STRUCTURE
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
SCRIPTS_CORPUS_DIR = join(SCRIPTS_DIR, 'corpora')
SCRIPTS_MOSAIC_DIR = join(SCRIPTS_DIR, 'mosaics')
SCRIPTS_AUDIO_DIR = join(SCRIPTS_DIR, 'audio')

# ------------------------------------- #
# DEFINE TEMPLATE SCRIPTS
# ------------------------------------- #

TEMPLATES = {
    "corpus": {
        "corpus": {
            "name": f"{TEST_NAME}-corpus",
            "source": [
                join(AUDIO_IN_DIR, "source.wav")
            ],
            "features": [
                "timbre"
            ]
        }
    },
    "mosaic": {
        "mosaic": {
            "name": f"{TEST_NAME}-mosaic",
            "target": join(AUDIO_IN_DIR, "target.wav"),
            "corpus": [
                join(CORPUS_DIR, f"{TEST_NAME}-corpus.gamut")
            ]
        }
    },
    "audio": {
        "audio": {
            "name": f"{TEST_NAME}-audio",
            "mosaic": join(MOSAIC_DIR, f"{TEST_NAME}-mosaic.gamut"),
            "fidelity": 1.0,
            "grain_dur": 0.1,
            "grain_env": "cosine",
            "corpus_weights": 1.0,
            "stretch_factor": 1.0,
            "pan_depth": 3,
            "n_chans": 2,
            "onset_var": 0,
            "play": False,
        }
    }
}

TEMPLATES[TEST_NAME] = {k: TEMPLATES[k][k] for k in TEMPLATES}

# ------------------------------------- #
# INIT FLAG
# ------------------------------------- #

if args.init:
    for x in [GAMUT_DIR, MOSAIC_DIR, CORPUS_DIR, AUDIO_DIR, AUDIO_OUT_DIR, AUDIO_IN_DIR, SCRIPTS_DIR]:
        if not exists(x):
            makedirs(x)
    new_template(TEST_NAME)

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


# ------------------------------------- #
# CREATE TEMPLATE
# ------------------------------------- #

elif args.template:
    new_template(args.template)
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
                c.write(output_name)

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
                m.write(splitext(output_name)[0] + '.gamut')

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
                chdir(AUDIO_OUT_DIR)
                if convolve:
                    audio.convolve(**convolve)
                audio.write(splitext(output_name)[0] + '.wav')
                if args.play or play:
                    audio.play()
    exit()
else:
    throw("You didn't provide any arguments. Use -h or --help to learn more.")
