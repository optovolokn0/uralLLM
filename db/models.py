from sqlalchemy import Column, Integer, Text, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class VKGroup(Base):
    __tablename__ = "vk_groups"

    id = Column(Integer, primary_key=True)
    vk_group_id = Column(String, unique=True)
    name = Column(String)

class RawPost(Base):
    __tablename__ = "raw_posts"

    id = Column(Integer, primary_key=True)
    vk_post_id = Column(String, unique=True)
    group_id = Column(Integer, ForeignKey("vk_groups.id"))
    raw_text = Column(Text)
    post_date = Column(DateTime)
    likes = Column(Integer)


