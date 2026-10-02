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

# --- Patch MicroTeX and cmake warning suppressions ---
try:
    p_gb = os.path.join(scriptPath, 'ThirdParty', 'MicroTeX', 'src', 'graphic', 'graphic_basic.h')
    if os.path.isfile(p_gb):
        with open(p_gb, 'r', encoding='utf-8') as f:
            c = f.read()
        c = re.sub(r'float\s+lineWidth;\s+float\s+miterLimit;\s+Cap\s+cap;\s+Join\s+join;', 'float lineWidth;\n  Cap cap;\n  Join join;\n  float miterLimit;', c)
        with open(p_gb, 'w', encoding='utf-8') as f:
            f.write(c)

    p_gh = os.path.join(scriptPath, 'ThirdParty', 'MicroTeX', 'src', 'graphic', 'graphic.h')
    if os.path.isfile(p_gh):
        with open(p_gh, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'virtual ~TextLayout() = default;' not in c:
            c = c.replace('class TextLayout {\npublic:', 'class TextLayout {\npublic:\n  virtual ~TextLayout() = default;')
        if 'virtual ~Graphics2D() = default;' not in c:
            c = c.replace('class Graphics2D {\npublic:', 'class Graphics2D {\npublic:\n  virtual ~Graphics2D() = default;')
        with open(p_gh, 'w', encoding='utf-8') as f:
            f.write(c)

    p_gqt = os.path.join(scriptPath, 'ThirdParty', 'MicroTeX', 'src', 'platform', 'qt', 'graphic_qt.h')
    if os.path.isfile(p_gqt):
        with open(p_gqt, 'r', encoding='utf-8') as f:
            c = f.read()
        if 'virtual ~TextLayout_qt() = default;' not in c:
            c = c.replace('TextLayout_qt(const std::wstring& src, const sptr<Font_qt>& font);', 'TextLayout_qt(const std::wstring& src, const sptr<Font_qt>& font);\n  virtual ~TextLayout_qt() = default;')
        if 'virtual ~Graphics2D_qt() = default;' not in c:
            c = c.replace('Graphics2D_qt(QPainter* painter);', 'Graphics2D_qt(QPainter* painter);\n  virtual ~Graphics2D_qt() = default;')
        with open(p_gqt, 'w', encoding='utf-8') as f:
            f.write(c)

    p_opt = os.path.join(scriptPath, '..', 'cmake', 'options_win.cmake')
    if os.path.isfile(p_opt):
        with open(p_opt, 'r', encoding='utf-8') as f:
            c = f.read()
        c = c.replace('/w15038', '/wd5038')
        c = c.replace('/w14265', '/wd4265')
        c = re.sub(r'(\s+)/WX(\s+)', r'\1/WX-\2', c)
        with open(p_opt, 'w', encoding='utf-8') as f:
            f.write(c)

    print('[PATCH] MicroTeX headers and cmake options patched successfully.', flush=True)
except Exception as e:
    print('[PATCH WARNING] ' + str(e), flush=True)
# ---------------------------------------------------

finish(run_cmake.run(scriptName, arguments))
