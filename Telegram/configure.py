'''
This file is part of Telegram Desktop,
the official desktop application for the Telegram messaging service.

For license and copyright information please follow this link:
https://github.com/telegramdesktop/tdesktop/blob/master/LEGAL
'''
import sys, os, re

sys.dont_write_bytecode = True
scriptPath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(scriptPath + '/../cmake')
import run_cmake
sys.path.append(scriptPath + '/build')
import qt_version

executePath = os.getcwd()
def finish(code):
    global executePath
    os.chdir(executePath)
    sys.exit(code)

def error(message):
    print('[ERROR] ' + message)
    finish(1)

if sys.platform == 'win32' and 'COMSPEC' not in os.environ:
    error('COMSPEC environment variable is not set.')

scriptName = os.path.basename(scriptPath)

arguments = sys.argv[1:]

officialTarget = ''
officialTargetFile = scriptPath + '/build/target'
if os.path.isfile(officialTargetFile):
    with open(officialTargetFile, 'r') as f:
        for line in f:
            officialTarget = line.strip()

arch = ''
if officialTarget in ['win', 'uwp']:
    arch = 'x86'
elif officialTarget in ['win64', 'uwp64']:
    arch = 'x64'
elif officialTarget in ['winarm', 'uwparm']:
    arch = 'arm'
if not qt_version.resolve(arch):
    error('Unsupported platform.')

if 'qt6' in arguments:
    arguments.remove('qt6')

if officialTarget != '':
    officialApiIdFile = scriptPath + '/../../DesktopPrivate/custom_api_id.h'
    if not os.path.isfile(officialApiIdFile):
        error('DesktopPrivate/custom_api_id.h not found.')
    with open(officialApiIdFile, 'r') as f:
        for line in f:
            apiIdMatch = re.search(r'ApiId\s+=\s+(\d+)', line)
            apiHashMatch = re.search(r'ApiHash\s+=\s+"([a-fA-F\d]+)"', line)
            if apiIdMatch:
                arguments.append('-DTDESKTOP_API_ID=' + apiIdMatch.group(1))
            elif apiHashMatch:
                arguments.append('-DTDESKTOP_API_HASH=' + apiHashMatch.group(1))
    if arch != '':
        arguments.append(arch)

# Patch MicroTeX struct Stroke member initialization order
microtex_header = os.path.join(scriptPath, 'ThirdParty', 'MicroTeX', 'src', 'graphic', 'graphic_basic.h')
if os.path.isfile(microtex_header):
    try:
        with open(microtex_header, 'r', encoding='utf-8') as f:
            c = f.read()
        c = re.sub(
            r'float\s+lineWidth;\s+float\s+miterLimit;\s+Cap\s+cap;\s+Join\s+join;',
            'float lineWidth;\n  Cap cap;\n  Join join;\n  float miterLimit;',
            c
        )
        with open(microtex_header, 'w', encoding='utf-8') as f:
            f.write(c)
        print('[PATCH] MicroTeX graphic_basic.h patched.')
    except Exception as e:
        print('[PATCH WARNING] Failed to patch MicroTeX: ' + str(e))

# Replace /w15038 with /wd5038 in cmake/options_win.cmake
options_win_path = os.path.join(scriptPath, '..', 'cmake', 'options_win.cmake')
if os.path.isfile(options_win_path):
    try:
        with open(options_win_path, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('/w15038', '/wd5038')
        with open(options_win_path, 'w', encoding='utf-8') as f:
            f.write(c)
        print('[PATCH] cmake/options_win.cmake patched (/wd5038).')
    except Exception as e:
        print('[PATCH WARNING] Failed to patch options_win.cmake: ' + str(e))

finish(run_cmake.run(scriptName, arguments))
