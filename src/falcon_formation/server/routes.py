"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import concurrent.futures

from flask import Response, abort, request

from falcon_formation.falcon_formation import create_teams, get_goalie_number, get_teams
from falcon_formation.server import parse_search_parameters, server


@server.route("/")
def home() -> str:
    """Home."""
    # TODO: Add number of teams and the number of team distributions that have been generated.
    return "Application is working."


@server.route("/create_teams/")
def create_teams_route() -> Response:
    """Create teams."""
    team_id_value = parse_search_parameters(request.query_string.decode()).get("team_id")
    if team_id_value is None:
        abort(400, "Missing team id")
    team_id = int(team_id_value)

    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(create_teams, team_id)

    return Response("Creating teams...", content_type="text/plain; charset=utf-8")


@server.route("/get_teams/")
def get_teams_route() -> Response:
    """Get teams."""
    team_id_value = parse_search_parameters(request.query_string.decode()).get("team_id")
    if team_id_value is None:
        abort(400, "Missing team id")
    team_id = int(team_id_value)
    show_skill = parse_search_parameters(request.query_string.decode()).get("show_skill", "true").lower() == "true"
    show_position = (
        parse_search_parameters(request.query_string.decode()).get("show_position", "true").lower() == "true"
    )
    show_guest = parse_search_parameters(request.query_string.decode()).get("show_guest", "true").lower() == "true"

    return Response(
        get_teams(team_id, show_skill, show_position, show_guest),
        content_type="text/plain; charset=utf-8",
    )


@server.route("/get_goalie_number/")
def get_goalie_number_route() -> Response:
    """Get goalie number."""
    team_id_value = parse_search_parameters(request.query_string.decode()).get("team_id")
    if team_id_value is None:
        abort(400, "Missing team id")
    team_id = int(team_id_value)

    return Response(get_goalie_number(team_id), content_type="text/plain; charset=utf-8")
