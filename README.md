## <div align="center"> 🦅 falcon-formation</div>

<div align="center">
<a href="https://github.com/daniel-mizsak/falcon-formation/actions/workflows/ci.yml" target="_blank"><img src="https://github.com/daniel-mizsak/falcon-formation/actions/workflows/ci.yml/badge.svg" alt="build status"></a>
<a href="https://codecov.io/gh/daniel-mizsak/falcon-formation" target="_blank"><img src="https://codecov.io/gh/daniel-mizsak/falcon-formation/graph/badge.svg?token=LHJWFDHYJP"/></a>
<a href="https://results.pre-commit.ci/latest/github/daniel-mizsak/falcon-formation/main" target="_blank"><img src="https://results.pre-commit.ci/badge/github/daniel-mizsak/falcon-formation/main.svg" alt="pre-commit.ci status"></a>
<a href="https://img.shields.io/github/license/daniel-mizsak/falcon-formation" target="_blank"><img src="https://img.shields.io/github/license/daniel-mizsak/falcon-formation" alt="license"></a>
</div>

## Overview
Create evenly distributed hockey teams.


## Getting started
The program works by getting the registered players for the given day's practice through the [holdsport api](https://github.com/Holdsport/holdsport-api), and takes the corresponding players from a local file where their preferred position and skill level is stored.

Then the teams are generated so that:
- The number of players in each team is as equal as possible
- The sum of the skill levels in each team is as equal as possible
- The number of goalkeepers in each team is as equal as possible
- The number of defensive players in each team is as equal as possible

If there are multiple possible solutions a team is randomly picked.
Finally the teams are sent in a Telegram message to the coach. ([As holdsport does not support the chat functionality of an event.](https://github.com/Holdsport/holdsport-api/issues/20))
