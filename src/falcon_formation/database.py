"""
Class for storing and loading data from a MongoDB database.

@author "Daniel Mizsak" <info@pythonvilag.hu>
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pymongo.mongo_client import MongoClient

from falcon_formation.data_models import Guest, Member, TeamDistribution, TeamMetadata

if TYPE_CHECKING:
    from pymongo.results import DeleteResult, InsertOneResult, UpdateResult


class FalconFormationDatabase:
    """Class for MongoDB database connection and operations."""

    TEAM_METADATA_DATABASE_NAME = "falcon_formation"
    TEAM_METADATA_COLLECTION_NAME = "team_metadata"

    MEMBER_COLLECTION_NAME = "members"
    GUEST_COLLECTION_NAME = "guests"
    TEAM_DISTRIBUTION_COLLECTION_NAME = "team_distributions"

    def __init__(
        self: FalconFormationDatabase,
        client: MongoClient[Any] | None = None,
        host: str | None = None,
        port: int | None = None,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Create the MongoDB client and connect to the database."""
        if client is None:
            self.client: MongoClient[Any] = MongoClient(
                host=host,
                port=port,
                username=username,
                password=password,
            )  # pragma: no cover
        else:
            self.client = client
        self.team_metadata_collection = self.client[self.TEAM_METADATA_DATABASE_NAME][
            self.TEAM_METADATA_COLLECTION_NAME
        ]

    # TeamMetadata
    def insert_team_metadata(self: FalconFormationDatabase, team_metadata: TeamMetadata) -> InsertOneResult:
        """Insert team metadata into the database."""
        return self.team_metadata_collection.insert_one(team_metadata.to_dict())

    def update_team_metadata(self: FalconFormationDatabase, team_metadata: TeamMetadata) -> UpdateResult:
        """Update team metadata in the database."""
        return self.team_metadata_collection.update_one(
            {"_id": str(team_metadata._id)},  # noqa: SLF001
            {"$set": team_metadata.to_dict()},
        )

    def delete_team_metadata(self: FalconFormationDatabase, team_metadata: TeamMetadata) -> DeleteResult:
        """Delete team metadata from the database."""
        return self.team_metadata_collection.delete_one({"_id": str(team_metadata._id)})  # noqa: SLF001

    def team_metadata_exists(self: FalconFormationDatabase, _id: int) -> bool:
        """Check if team metadata exists in the database."""
        return self.team_metadata_collection.count_documents({"_id": str(_id)}) == 1

    def load_team_metadata(self: FalconFormationDatabase, _id: int) -> TeamMetadata | None:
        """Load team metadata from the database."""
        team_metadata = self.team_metadata_collection.find_one({"_id": str(_id)})
        if team_metadata is not None:
            return TeamMetadata.from_dict(team_metadata)
        return None

    # Member
    def insert_member(self: FalconFormationDatabase, team_id: int, member: Member) -> InsertOneResult:
        """Insert a member into the database."""
        team_collection = self.client[str(team_id)][self.MEMBER_COLLECTION_NAME]
        return team_collection.insert_one(member.to_dict())

    def update_member(self: FalconFormationDatabase, team_id: int, member: Member) -> UpdateResult:
        """Update a member in the database."""
        team_collection = self.client[str(team_id)][self.MEMBER_COLLECTION_NAME]
        return team_collection.update_one({"_id": str(member._id)}, {"$set": member.to_dict()})  # noqa: SLF001

    def delete_member(self: FalconFormationDatabase, team_id: int, member: Member) -> DeleteResult:
        """Delete a member from the database."""
        team_collection = self.client[str(team_id)][self.MEMBER_COLLECTION_NAME]
        return team_collection.delete_one({"_id": str(member._id)})  # noqa: SLF001

    def member_exists(self: FalconFormationDatabase, team_id: int, _id: int) -> bool:
        """Check if a member exists in the database."""
        team_collection = self.client[str(team_id)][self.MEMBER_COLLECTION_NAME]
        return team_collection.count_documents({"_id": str(_id)}) == 1

    def load_member(self: FalconFormationDatabase, team_id: int, _id: int) -> Member | None:
        """Load a member from the database."""
        team_collection = self.client[str(team_id)][self.MEMBER_COLLECTION_NAME]
        data = team_collection.find_one({"_id": str(_id)})
        return Member.from_dict(data) if data else None

    def load_member_collection(self: FalconFormationDatabase, team_id: int) -> list[Member]:
        """Load all members from the database."""
        team_collection = self.client[str(team_id)][self.MEMBER_COLLECTION_NAME]
        return sorted([Member.from_dict(data) for data in team_collection.find()], key=lambda member: member.name)

    # Guest
    def insert_guest(
        self: FalconFormationDatabase,
        team_id: int,
        date: str,
        guest: Guest,
    ) -> InsertOneResult:
        """Insert a guest into the database."""
        team_collection = self.client[str(team_id)][f"{self.GUEST_COLLECTION_NAME}_{date}"]
        return team_collection.insert_one(guest.to_dict())

    def delete_guest(self: FalconFormationDatabase, team_id: int, date: str, guest: Guest) -> DeleteResult:
        """Delete a guest from the database."""
        team_collection = self.client[str(team_id)][f"{self.GUEST_COLLECTION_NAME}_{date}"]
        return team_collection.delete_one({"_id": guest.name})

    def load_guest(self: FalconFormationDatabase, team_id: int, date: str, _id: str) -> Guest | None:
        """Load a guest from the database."""
        team_collection = self.client[str(team_id)][f"{self.GUEST_COLLECTION_NAME}_{date}"]
        data = team_collection.find_one({"_id": str(_id)})
        if data:
            return Guest.from_dict(data)
        return None

    def load_guest_collection(self: FalconFormationDatabase, team_id: int, date: str) -> list[Guest]:
        """Load all guests from the database."""
        team_collection = self.client[str(team_id)][f"{self.GUEST_COLLECTION_NAME}_{date}"]
        return sorted([Guest.from_dict(data) for data in team_collection.find()], key=lambda guest: guest.name)

    # TeamDistribution
    def insert_or_update_team_distribution(
        self: FalconFormationDatabase,
        team_id: int,
        team_distribution: TeamDistribution,
    ) -> UpdateResult:
        """Insert or update a team distribution in the database."""
        team_collection = self.client[str(team_id)][self.TEAM_DISTRIBUTION_COLLECTION_NAME]
        return team_collection.update_one(
            {"_id": team_distribution.date},
            {"$set": team_distribution.to_dict()},
            upsert=True,
        )

    def load_team_distribution(
        self: FalconFormationDatabase,
        team_id: int,
        _id: str,
    ) -> TeamDistribution | None:
        """Load a team distribution from the database."""
        team_collection = self.client[str(team_id)][self.TEAM_DISTRIBUTION_COLLECTION_NAME]
        data = team_collection.find_one({"_id": _id})
        if data is not None:
            return TeamDistribution.from_dict(data)
        return None
