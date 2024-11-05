from pathlib import Path

from flask import Flask, redirect, send_file
from werkzeug import Response

server = Flask(__name__)
available_teams = ["falcons_1"]


@server.route("/")
def home() -> str:
    """Home page of the server."""
    return "The app is working!"


@server.route("/teams/<team>")
def redirect_to_team(team: str) -> Response:
    """Redirect to the team-specific dashboard.

    Args:
        team (str): Team name.

    Returns:
        Response: Redirect response to the team-specific dashboard.
    """
    if team not in available_teams:
        return redirect("/")
    return redirect(f"/add_guests/{team}")


@server.route("/extras/<team_name>/<practice_date>")
def serve_json(team_name: str, practice_date: str) -> Response:
    """Serve the JSON file containing the extra players for the given team and practice date.

    Args:
        team_name (str): Name of the team.
        practice_date (str): Date of the practice in the format "YYYY-MM-DD".

    Returns:
        Response: JSON file containing the extra players for the given date.
    """
    file_path = Path(f"data/extras/{team_name.upper()}_{practice_date}.json").resolve()
    return send_file(file_path, mimetype="application/json")


from falcon_formation.server.add_guests import add_guests_app
from falcon_formation.server.register_winner import register_winner_app
