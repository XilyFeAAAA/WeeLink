#! /usr/bin/env python
# -*- coding: utf-8 -*-#-
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base

class Account(Base):
    """微信账户信息表"""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(String(100), nullable=True)
    wxid: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    nickname: Mapped[str] = mapped_column(String(100), nullable=True)
    alias: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    device_name: Mapped[str] = mapped_column(String(100), nullable=True)
    device_id: Mapped[str] = mapped_column(String(100), nullable=True)
