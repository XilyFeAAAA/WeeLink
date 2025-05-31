#! /usr/bin/env python
# -*- coding: utf-8 -*-#-
from src import config
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
    f"mysql+aiomysql://"
    f"{config.MYSQL_USER}:{config.MYSQL_PASSWORD}"
    f"@{config.MYSQL_HOST}/{config.MYSQL_DB}"
)


async_session = async_sessionmaker(async_engine, expire_on_commit=False)
