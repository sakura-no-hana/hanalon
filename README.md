# Hanalon
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/discord/715607808028049459.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/wKqGrKN)

Hanalon is an RPG Discord bot.
## Requirements
- Docker [(?)](https://docs.docker.com/get-docker/) *

\* You don't *need* Docker, but it makes setting stuff up easier.
## Usage
There are a few steps to set up this Discord bot locally.
- Register a Discord bot.
- Create a MongoDB Atlas instance (or anything that will give you a MongoDB connection URI).
- Modify the `config.yaml` file. `token` is your bot token, `mongo` is your MongoDB connection URI, `guild` is the guild ID you plan on testing with, `devs` is a list of the developers' user IDs.
- `cd` into the parent directory of `src/`. This directory should look something like this:
```
hanalon
├── Dockerfile
├── Pipfile
├── config.yaml
├── requirements.txt
├── run.sh
⋮
└── src
    ├── __main__.py
    ├── cogs
    │   ⋮
    │
    └── utils
        ⋮
```

**Docker:**
- Run `run.sh`. You may need to `chmod` to be able to run it. Alternatively, you can paste the commands into your console.

**No Docker:**
- Depending on what kind of environment you have, either run `pipenv install` or `pip install -r requirements.txt`.
- `cd` into the parent directory of `src/`. This directory should look something like this:
```
src
├── __main__.py
├── cogs
│   ⋮
│
└── utils
    ⋮
```
- Run `python3 __main__.py`.
## Contributing
Pull requests are always welcome. Please open an issue so that other contributors may fix an issue if you are unable to fix it yourself. For feature requests and the like, please open issues.

Keep in mind that even as a side-project, we have standards here. Thus, we've set up a pre-commit config file for your use. We currently only run a check with `black`, but the pre-commit hook makes sure that your code has sorted imports, is black compliant, and that your requirements.txt matches your Pipfile.lock. Testing is preferable to no testing, but we understand that it can be difficult to automate testing with a primarily visual application.
