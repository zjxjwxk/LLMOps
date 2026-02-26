#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@Author :   Xinkang Wu
@Time   :   2026/2/21 19:29
@File   :   app.py
"""
import dotenv
from flask_migrate import Migrate
from injector import Injector

from app.http.module import ExtensionModule
from config import Config
from internal.router import Router
from internal.server import Http
from pkg.sqlalchemy import SQLAlchemy

# 将.env文件加载到环境变量中
dotenv.load_dotenv()

# 应用配置
config = Config()

# 依赖注入
injector = Injector([ExtensionModule])

app = Http(
    __name__,
    config=config,
    db=injector.get(SQLAlchemy),
    migrate=injector.get(Migrate),
    router=injector.get(Router)
)

if __name__ == "__name__":
    app.run(debug=True)
