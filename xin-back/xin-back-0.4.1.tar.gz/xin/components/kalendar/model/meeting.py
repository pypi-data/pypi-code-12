from umongo import Document, Schema, fields
from .database import db


class Meeting(Document):

    class Schema(Schema):
        calendar = fields.ReferenceField("Calendar", required=True)
        name = fields.StringField(max_length=120, required=True)
        users = fields.ListField(fields.EmailField(max_length=255), required=True)
        begin = fields.DateTimeField(required=True)
        duration = fields.IntField(required=True)
        place = fields.StringField(max_length=255)
        tags = fields.ListField(fields.StringField(max_length=20))
        comment = fields.StringField(max_length=255)

    class Config:
        collection = db.meeting
