"""
Load the latest artifact from the code's repository containing the generated team data.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import io
import zipfile

import requests

STATUS_CODE_OK = 200


def get_artifact_data(api_pat: str) -> str:
    """Return the output message of the most recently generated team data.

    Args:
        api_pat (str): The personal access token for the GitHub API.

    Returns:
        str: The content of the latest artifact. If no artifact is found, an empty string is returned.
    """
    artifact_content = _get_latest_artifact(api_pat)
    if artifact_content is None:
        return ""

    with zipfile.ZipFile(io.BytesIO(artifact_content), "r") as zip_reference:
        file_name = zip_reference.namelist()[0]
        with zip_reference.open(file_name) as f:
            return f.read().decode("utf-8")


def _get_latest_artifact(api_pat: str) -> bytes | None:
    """Return the content of the latest artifact from the code's repository.

    Args:
        api_pat (str): The personal access token for the GitHub API.

    Returns:
        bytes | None: The content of the latest artifact, or None if no artifact is found.
    """
    owner = "daniel-mizsak"
    repo = "falcon-formation"
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/artifacts"

    response = requests.get(url, timeout=5)
    if response.status_code != STATUS_CODE_OK:
        return None

    artifacts = response.json()["artifacts"]
    artifact_url = artifacts[0]["archive_download_url"]
    headers = {"Authorization": f"Bearer {api_pat}"}

    artifact_response = requests.get(artifact_url, headers=headers, timeout=5)
    if artifact_response.status_code != STATUS_CODE_OK:
        return None

    return artifact_response.content
