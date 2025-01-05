[![Test wtf](https://github.com/Asugawara/WhatTheFuck/actions/workflows/run_test.yml/badge.svg)](https://github.com/Asugawara/WhatTheFuck/actions/workflows/run_test.yml)
![PyPI](https://img.shields.io/pypi/v/wtf-cli?color=green)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/wtf-cli)
![GitHub](https://img.shields.io/github/license/Asugawara/WhatTheFuck)

# WhatTheFuck

**WhatTheFuck** is a command-line tool that leverages LLMs to correct and enhance previously executed terminal commands. Inspired by [`wut`](https://github.com/shobrook/wut) and [`The Fuck`](https://github.com/nvbn/thefuck), it’s designed to save your time and sanity by fixing errors, summarizing logs, and more.

# Example
```bash
$ (wtf): git brnch
git: 'brnch' is not a git command. See 'git --help'.

The most similar command is
	branch
$ (wtf): wtf
The error message indicates that 'brnch' is not recognized as a valid Git command. The correct command is 'branch', which is likely what you intended to use to list, create,
or delete branches in your repository. The suggestion for 'branch' highlights this common typo. To avoid such errors, ensure command spelling is accurate.
Run `git branch`? [y/N]: y
* main
```
※LLM's streamed outputs are omitted for simplicity

# Features

- **LLM Switching**: Easily switch between different llms.(OpanAI, Anthropic, Vertex)
- **Instant Command Fixes**: Detect and fix incorrect terminal commands effortlessly.
- **One-Click Execution**: Run corrected commands seamlessly.
- **Log Summarization**: Summarize logs from previous terminal commands for quick insights.

> [!NOTE]
> WTF utilizes [`script(Unix)`](https://en.wikipedia.org/wiki/Script_(Unix)) to log and analyze the previously executed command.

# Installation
```bash
$ pip install wtf-cli
# or
$ uv add wtf-cli
# or
$ poetry add wtf-cli
```



# Versioning
This repo uses [Semantic Versioning](https://semver.org/).

# License
**WhatTheFuck** is released under the MIT License. See [LICENSE](/LICENSE) for additional details.
