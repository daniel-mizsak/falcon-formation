"""
Short description and source of base code.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import concurrent.futures

from flask import Response, abort, request

from falcon_formation.main import create_teams, get_goalie_number, get_teams
from falcon_formation.server import parse_search_parameters, server


@server.route("/")
def home() -> str:
    """Home."""
    return "Application is working."


@server.route("/create_teams")
def create_teams_route() -> Response:
    """Create teams."""
    team_id = parse_search_parameters(request.query_string.decode())
    if not team_id:
        abort(400, "Missing team id")

    executor = concurrent.futures.ThreadPoolExecutor()
    executor.submit(create_teams, team_id)

    return Response("Creating teams...", content_type="text/plain")


@server.route("/get_teams")
def get_teams_route() -> Response:
    """Get teams."""
    team_id = parse_search_parameters(request.query_string.decode())
    if not team_id:
        abort(400, "Missing team id")

    return Response(get_teams(team_id), content_type="text/plain")


@server.route("/get_goalie_number")
def get_goalie_number_route() -> Response:
    """Get goalie number."""
    team_id = parse_search_parameters(request.query_string.decode())
    if not team_id:
        abort(400, "Missing team id")

    return Response(get_goalie_number(team_id), content_type="text/plain")
