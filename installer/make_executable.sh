# Source the virtual env
source "/c/Users/Margaux TAMIC/PycharmProjects/skribble/venv/Scripts/activate"

# shellcheck disable=SC2164
cd "/c/Users/Margaux TAMIC/PycharmProjects/skribble/installer"

# Generate executable from python
pyinstaller --noconfirm --noconsole --clean "/c/Users/Margaux TAMIC/PycharmProjects/skribble/installer/launcher.spec"
