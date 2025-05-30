#! /usr/bin/env python
# -*- coding: utf-8 -*-#-
from src.config import conf
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
    f"mysql+aiomysql://"
    f"{conf().get('MYSQL_USER')}:{conf().get('MYSQL_PASSWORD')}"
    f"@{conf().get('MYSQL_HOST')}/{conf().get('MYSQL_DB')}"
)


async_session = async_sessionmaker(async_engine, expire_on_commit=False)
