# Hanalon
Hanalon is a RPG Discord bot.
## Requirements
- Bash (?)
- Docker (?)

You don't strictly need these. You can use the Docker dashboard to fire up the containers, or you could just not use containers at all and, I dunno, use a venv. How to do those things, though, is beyond the scope of this file.
## Usage
There are a few steps to set up this Discord bot locally.
1. Register a Discord bot.
2. Create a MongoDB Atlas instance (or anything that will give you a MongoDB connection URI).
3. Create a `.env` file. You will need 2 things in it: your Discord bot token, `TOKEN`, and your MongoDB connection URI, `MONGO`. This file should be located in the same directory as `src/`.
4. `cd` into the parent directory of `src/` and run `run.sh`. You may need to `chmod` to be able to run it.
## Contributing
Pull requests are always welcome. Please open an issue so that other contributors may fix an issue if you are unable to fix it yourself. For feature requests and the like, please open issues. Testing is not required (testing with an external service is a pain), but is preferable.
