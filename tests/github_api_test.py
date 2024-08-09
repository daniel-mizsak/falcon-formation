"""
Tests for the github api module.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

import io
import zipfile

import requests_mock
from falcon_formation.github_api import _get_latest_artifact, get_artifact_data


def test_get_artifact_data() -> None:
    artifact_content = b"Hello, World!"
    zipped_content = io.BytesIO()
    with zipfile.ZipFile(zipped_content, "w") as zipf:
        zipf.writestr("test.txt", artifact_content)
    zipped_content.seek(0)

    with requests_mock.Mocker() as m:
        m.get(
            "https://api.github.com/repos/daniel-mizsak/falcon-formation/actions/artifacts",
            json={"artifacts": [{"archive_download_url": "http://example.com/artifact.zip"}]},
        )
        m.get(
            "http://example.com/artifact.zip",
            content=zipped_content.read(),
        )

        result = get_artifact_data("api_pat")
    assert result == "Hello, World!"


def test_get_latest_artifact() -> None:
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.github.com/repos/daniel-mizsak/falcon-formation/actions/artifacts",
            json={
                "artifacts": [
                    {
                        "id": 1,
                        "name": "team_data",
                        "size_in_bytes": 1000,
                        "archive_download_url": "https://api.github.com/repos/daniel-mizsak/falcon-formation/actions/artifacts/1",
                    },
                ],
            },
        )
        m.get(
            "https://api.github.com/repos/daniel-mizsak/falcon-formation/actions/artifacts/1",
            content=b"artifact_content",
        )
        artifact_content = _get_latest_artifact("api_pat")
        assert artifact_content == b"artifact_content"
