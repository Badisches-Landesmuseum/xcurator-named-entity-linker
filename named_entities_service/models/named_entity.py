from typing import Optional

from bson import ObjectId
from bson.errors import InvalidId
from pydantic import Field
from datetime import datetime

from models.entity_type import EntityType
from models.mongo_model import MongoModel
from proto.dreipc.asset.document.namedentities import NamedEntityProto


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        try:
            return ObjectId(str(v))
        except InvalidId:
            raise ValueError("Not a valid ObjectId")


class NamedEntity(MongoModel):
    id: Optional[ObjectId] = Field(alias="_id")
    source_id: Optional[str]
    literal: str
    start_position: int
    end_position: int
    type: EntityType
    knowledge_base_id: Optional[str]
    knowledge_base_url: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def proto(self):
        return NamedEntityProto(id=str(self.id),
                                literal=self.literal,
                                source_id=self.source_id,
                                type=self.type,
                                start_position=self.start_position,
                                end_position=self.end_position,
                                knowledge_base_id=self.knowledge_base_id,
                                knowledge_base_url=self.knowledge_base_url)
