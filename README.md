# Hanalon
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Discord](https://img.shields.io/discord/715607808028049459.svg?label=&logo=discord&logoColor=ffffff&color=7389D8&labelColor=6A7EC2)](https://discord.gg/vpEv3HJ)

Hanalon is a RPG Discord bot.
## Requirements
- Bash [(?)](https://www.gnu.org/software/bash/manual/html_node/Installing-Bash.html)
- Docker [(?)](https://docs.docker.com/get-docker/)
## Usage
There are a few steps to set up this Discord bot locally.
- Register a Discord bot.
- Create a MongoDB Atlas instance (or anything that will give you a MongoDB connection URI).
- Modify the `config.yaml` file. `token` is your bot token, `mongo` is your MongoDB connection URI, `guild` is the guild ID you plan on testing with, `devs` is a list of the developers' user IDs.
- `cd` into the parent directory of `src/` and run `run.sh`. You may need to `chmod` to be able to run it.
## Contributing
Pull requests are always welcome. Please open an issue so that other contributors may fix an issue if you are unable to fix it yourself. For feature requests and the like, please open issues. Testing is not required (testing with an external service is a pain), but it would be nice to have.
