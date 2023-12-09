

# make pyenv

## Windows
```cmd
pyenv-venv install 3.11.6 fsd
pyenv-venv activate fsd
```
## Linux
```cmd
pyenv virtualenv 3.11.6 fsd
# pyenv activate fsd  # does not add (fsd) to terminal
source ${VA_TOOLS_USER_DIR}/.pyenv/versions/fsd/bin/activate
```

# clone repo and install dependencies

```bash
dnd
git clone https://github.com/pbk0/feature_selection_dlsca
cd feature_selection_dlsca/

```