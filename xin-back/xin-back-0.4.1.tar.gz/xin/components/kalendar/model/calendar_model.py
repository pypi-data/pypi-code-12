from umongo import Document, Schema, fields
from .database import db


class Calendar(Document):

    class Schema(Schema):
        name = fields.StrField(required=True)
        users = fields.ListField(fields.EmailField(max_length=255), required=True)
        meetings = fields.ListField(fields.ReferenceField("Meeting"))

    class Config:
        collection = db.calendar
