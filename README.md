## <div align="center">🦅 falcon-formation</div>
<div align="center">
    <kbd>
        <a href="https://github.com/daniel-mizsak/falcon-formation/actions/workflows/ci.yml" target="_blank"><img src="https://github.com/daniel-mizsak/falcon-formation/actions/workflows/ci.yml/badge.svg" alt="build status"></a>
        <a href="https://codecov.io/gh/daniel-mizsak/falcon-formation" target="_blank"><img src="https://codecov.io/gh/daniel-mizsak/falcon-formation/graph/badge.svg?token=YLG2N7W3O1"/></a>
        <a href="https://results.pre-commit.ci/latest/github/daniel-mizsak/falcon-formation/main" target="_blank"><img src="https://results.pre-commit.ci/badge/github/daniel-mizsak/falcon-formation/main.svg" alt="pre-commit.ci status"></a>
        <a href="https://img.shields.io/github/license/daniel-mizsak/falcon-formation" target="_blank"><img src="https://img.shields.io/github/license/daniel-mizsak/falcon-formation" alt="license"></a>
    </kbd>
</div>


## Overview
Create evenly distributed hockey teams.


## Getting started
To use the `falcon-formation` bot and automatically generate teams for your practices, the following steps are needed:
- Add `Bot Falcon Formation` to you Holdsport team. It does NOT need admin rights and it will not register to any practice, nor will it pay membership fee, but this is needed to query the registered players for every event.
- Fill out a Google Sheet form with data about your players. The skill can be self-assigned or determined by the coach, but the names should not be changed and the `Positions` field should be filled according to the examples.
- Create a Telegram channel and add `@falcon_formation_bot` to it. It is recommended to add multiple people so that the message is ensured to be forwarded to holdsports. The ID of the channel is needed for the message delivery. (From experience it looks like that when a group reaches 10 members, the ID of the conversation changes so it has to be updated.)
- Share some final minor details, such as how much time before each practice should the bot fire and what jersey colors are used by the teams.


## How does it work?
The program works by getting the registered players for the given day's practice through the [holdsport api](https://github.com/Holdsport/holdsport-api), and taking the corresponding players from a local file where their preferred position and skill level is stored.

Then the teams are generated so that:
- The number of players in each team is as equal as possible
- The number of goalkeepers in each team is as equal as possible
- The number of defensive players in each team is as equal as possible
- The sum of the skill levels in each team is as equal as possible

If there are multiple possible solutions a team is randomly picked.
Finally the teams are sent in a Telegram message to the coach. ([As holdsport does not support the chat functionality of an event.](https://github.com/Holdsport/holdsport-api/issues/20))
