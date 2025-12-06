# models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from typing import Optional

from db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    firebase_uid = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    display_name = Column(String, nullable=True)

    # 1:1 관계 (한 유저당 선호 설정 1개)
    preference = relationship("UserPreference", back_populates="user", uselist=False)


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)  # "korean" 등
    address = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)


class UserPreference(Base):
    __tablename__ = "user_preferences"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    # "korean,snack" 이런 식으로 저장 (간단하게)
    default_categories = Column(String, nullable=True)

    user = relationship("User", back_populates="preference")
