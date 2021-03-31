# Hanalon
Hanalon is a RPG Discord bot.
## Requirements
- Bash [(?)](https://www.gnu.org/software/bash/manual/html_node/Installing-Bash.html)
- Docker [(?)](https://docs.docker.com/get-docker/)
## Usage
There are a few steps to set up this Discord bot locally.
- Register a Discord bot.
- Create a MongoDB Atlas instance (or anything that will give you a MongoDB connection URI).
- Create a `.env` file. You will need 2 things in it: your Discord bot token, `TOKEN`, and your MongoDB connection URI, `MONGO`. This file should be located in the same directory as `src/`. Here's an example: 
```
TOKEN=XXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXX
MONGO=mongodb+srv://X:X@X.XXXXX.mongodb.net/X
```
- `cd` into the parent directory of `src/` and run `run.sh`. You may need to `chmod` to be able to run it.
## Contributing
Pull requests are always welcome. Please open an issue so that other contributors may fix an issue if you are unable to fix it yourself. For feature requests and the like, please open issues. Testing is not required (testing with an external service is a pain), but it would be nice to have.
