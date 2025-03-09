"""
Tests for the MongoDB database.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from falcon_formation.data_models import Guest, Member, TeamDistribution, TeamMetadata
from falcon_formation.database import FalconFormationDatabase


# TeamMetadata
def test_insert_team_metadata(database: FalconFormationDatabase, team_metadata: TeamMetadata) -> None:
    insert_team_metadata_result = database.insert_team_metadata(team_metadata)
    assert insert_team_metadata_result.acknowledged is True
    assert insert_team_metadata_result.inserted_id == str(team_metadata._id)  # noqa: SLF001


def test_update_team_metadata(database: FalconFormationDatabase, team_metadata: TeamMetadata) -> None:
    database.insert_team_metadata(team_metadata)
    team_metadata.activity_name = "New Activity Name"
    update_team_metadata_result = database.update_team_metadata(team_metadata)
    assert update_team_metadata_result.acknowledged is True
    assert update_team_metadata_result.modified_count == 1


def test_delete_team_metadata(database: FalconFormationDatabase, team_metadata: TeamMetadata) -> None:
    delete_team_metadata_result = database.delete_team_metadata(team_metadata)
    assert delete_team_metadata_result.acknowledged is True
    assert delete_team_metadata_result.deleted_count == 0
    database.insert_team_metadata(team_metadata)
    delete_team_metadata_result = database.delete_team_metadata(team_metadata)
    assert delete_team_metadata_result.acknowledged is True
    assert delete_team_metadata_result.deleted_count == 1


def test_team_metadata_exists(database: FalconFormationDatabase, team_metadata: TeamMetadata) -> None:
    team_metadata_exists_result = database.team_metadata_exists(team_metadata._id)  # noqa: SLF001
    assert team_metadata_exists_result is False
    database.insert_team_metadata(team_metadata)
    team_metadata_exists_result = database.team_metadata_exists(team_metadata._id)  # noqa: SLF001
    assert team_metadata_exists_result is True


def test_load_team_metadata(database: FalconFormationDatabase, team_metadata: TeamMetadata) -> None:
    load_team_metadata_result = database.load_team_metadata(team_metadata._id)  # noqa: SLF001
    assert load_team_metadata_result is None
    database.insert_team_metadata(team_metadata)
    load_team_metadata_result = database.load_team_metadata(team_metadata._id)  # noqa: SLF001
    assert load_team_metadata_result == team_metadata


# Member
def test_insert_member(database: FalconFormationDatabase, team_id: int, member: Member) -> None:
    insert_member_result = database.insert_member(team_id, member)
    assert insert_member_result.acknowledged is True
    assert insert_member_result.inserted_id == str(member._id)  # noqa: SLF001


def test_update_member(database: FalconFormationDatabase, team_id: int, member: Member) -> None:
    database.insert_member(team_id, member)
    member.name = "New Member Name"
    update_member_result = database.update_member(team_id, member)
    assert update_member_result.acknowledged is True
    assert update_member_result.modified_count == 1


def test_delete_member(database: FalconFormationDatabase, team_id: int, member: Member) -> None:
    delete_member_result = database.delete_member(team_id, member)
    assert delete_member_result.acknowledged is True
    assert delete_member_result.deleted_count == 0
    database.insert_member(team_id, member)
    delete_member_result = database.delete_member(team_id, member)
    assert delete_member_result.acknowledged is True
    assert delete_member_result.deleted_count == 1


def test_member_exists(database: FalconFormationDatabase, team_id: int, member: Member) -> None:
    member_exists_result = database.member_exists(team_id, member._id)  # noqa: SLF001
    assert member_exists_result is False
    database.insert_member(team_id, member)
    member_exists_result = database.member_exists(team_id, member._id)  # noqa: SLF001
    assert member_exists_result is True


def test_load_member(database: FalconFormationDatabase, team_id: int, member: Member) -> None:
    load_member_result = database.load_member(team_id, member._id)  # noqa: SLF001
    assert load_member_result is None
    database.insert_member(team_id, member)
    load_member_result = database.load_member(team_id, member._id)  # noqa: SLF001
    assert load_member_result == member


def test_load_member_collection(database: FalconFormationDatabase, team_id: int) -> None:
    load_member_collection_result = database.load_member_collection(team_id)
    assert load_member_collection_result == []
    member_1 = Member(_id=1234, name="Member Name 1")
    member_2 = Member(_id=1235, name="Member Name 2")
    database.insert_member(team_id, member_1)
    database.insert_member(team_id, member_2)
    load_member_collection_result = database.load_member_collection(team_id)
    assert load_member_collection_result == [member_1, member_2]


# Guest
def test_insert_guest(database: FalconFormationDatabase, team_id: int, date: str, guest: Guest) -> None:
    insert_guest_result = database.insert_guest(team_id, date, guest)
    assert insert_guest_result.acknowledged is True
    assert insert_guest_result.inserted_id == guest.name


def test_delete_guest(database: FalconFormationDatabase, team_id: int, date: str, guest: Guest) -> None:
    delete_guest_result = database.delete_guest(team_id, date, guest)
    assert delete_guest_result.acknowledged is True
    assert delete_guest_result.deleted_count == 0
    database.insert_guest(team_id, date, guest)
    delete_guest_result = database.delete_guest(team_id, date, guest)
    assert delete_guest_result.acknowledged is True
    assert delete_guest_result.deleted_count == 1


def test_load_guest(database: FalconFormationDatabase, team_id: int, date: str, guest: Guest) -> None:
    load_guest_result = database.load_guest(team_id, date, guest.name)
    assert load_guest_result is None
    database.insert_guest(team_id, date, guest)
    load_guest_result = database.load_guest(team_id, date, guest.name)
    assert load_guest_result == guest


def test_load_guest_collection(database: FalconFormationDatabase, team_id: int, date: str) -> None:
    load_guest_collection_result = database.load_guest_collection(team_id, date)
    assert load_guest_collection_result == []
    guest_1 = Guest(name="Guest Name 1")
    guest_2 = Guest(name="Guest Name 2")
    database.insert_guest(team_id, date, guest_1)
    database.insert_guest(team_id, date, guest_2)
    load_guest_collection_result = database.load_guest_collection(team_id, date)
    assert load_guest_collection_result == [guest_1, guest_2]


# TeamDistribution
def test_insert_or_update_team_distribution(
    database: FalconFormationDatabase,
    team_id: int,
    team_distribution: TeamDistribution,
) -> None:
    insert_team_distribution_result = database.insert_or_update_team_distribution(team_id, team_distribution)
    assert insert_team_distribution_result.acknowledged is True
    assert insert_team_distribution_result.upserted_id == team_distribution.date
    team_distribution.team_1.append(Member(_id=1238, name="Member Name 5"))
    update_team_distribution_result = database.insert_or_update_team_distribution(team_id, team_distribution)
    assert update_team_distribution_result.acknowledged is True
    assert update_team_distribution_result.modified_count == 1


def test_load_team_distribution(
    database: FalconFormationDatabase,
    team_id: int,
    team_distribution: TeamDistribution,
) -> None:
    load_team_distribution_result = database.load_team_distribution(team_id, team_distribution.date)
    assert load_team_distribution_result is None
    database.insert_or_update_team_distribution(team_id, team_distribution)
    load_team_distribution_result = database.load_team_distribution(team_id, team_distribution.date)
    assert load_team_distribution_result == team_distribution
