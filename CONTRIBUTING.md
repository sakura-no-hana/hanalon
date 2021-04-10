# Contributing

Pull requests are always welcome. Please open an issue so that other contributors may fix an issue if you are unable to fix it yourself. For feature requests and the like, please open issues.

Keep in mind that even as a side-project, we have standards here. Thus, we've set up a `.pre-commit-config.yaml` for your use. We currently only run a check with black, but the pre-commit hook makes sure that your code has sorted imports, is black compliant, and that your `requirements.txt` matches your `poetry.lock`. Testing is preferable to no testing, but we understand that it can be difficult to automate testing with a primarily visual application.

Dependencies are managed by Poetry, which uses `pyproject.toml`. Do not manually edit the `requirements.txt`; either let pre-commit do it for you, or run `poetry export -o requirements.txt --without-hashes`.
