# nuzlocke-tracker

cross-platform text-recognition-based nuzlocke tracker tool (WIP for platinum)

user note: either `config.defaults.json` or `config.json` may be edited to change the configuration of the tracker - `config.json` takes priority, so you can edit that to keep the default settings backed up in `config.defaults.json`, or you can just edit `config.defaults.json` directly if you don't care

dev note: duplicate `config.defaults.json` as `config.json` to change stuff locally without affecting the defaults for users


we're using pipenv to run this project (`pipenv install` to install dependencies, and `pipenv run python` where you would normally use `python` to run scripts), but this may work just fine if you have the appropriate packages availabe in another manner

note: all paths are relative to the top-level directory of the repo, so all scripts must be executed from said top-level directory

`src/main.py` is supposed to be the main process, which spawns a new window: press `q` to quit
`src/font/readfont.py` processes the fontfiles and separates the characters into their own files in `sprites/`
`src/font/readfont_index.py` does ...

TODO: write proper README for end-users, and installation/contribution guidelines, etc.


notes for devs:
we should probably consider setting up `make` to spit out .pyc files for many of the modules
we may want to try `cython` or `numba` for some of our slowest functions
