#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
文件提取器

@Author :   Xinkang Wu
@Time   :   2026/7/28 21:58
@File   :   file_extractor.py
"""
import os.path
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Union

import requests
from injector import inject
from langchain_community.document_loaders import UnstructuredExcelLoader, UnstructuredPDFLoader, \
    UnstructuredMarkdownLoader, UnstructuredHTMLLoader, UnstructuredCSVLoader, UnstructuredPowerPointLoader, \
    UnstructuredXMLLoader, UnstructuredFileLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document

from internal.model import UploadFile
from internal.service.oci_object_storage_service import OciObjectStorageService


@inject
@dataclass
class FileExtractor:
    """文件提取器，将远程文件或上传文件加载为LangChain文档或字符串"""

    oci_object_storage_service: OciObjectStorageService

    def load(
            self,
            upload_file: UploadFile,
            return_text: bool = False,
            is_unstructured: bool = True
    ) -> Union[list[Document], str]:
        """根据UploadFile记录，返回LangChain文档列表或字符串"""

        # 创建临时文件夹
        with tempfile.TemporaryDirectory() as temp_dir:
            # 构建临时文件路径
            file_path = os.path.join(temp_dir, os.path.basename(upload_file.key))

            # 从对象存储服务下载文件到临时文件路径
            self.oci_object_storage_service.download_file(upload_file.key, file_path)

            # 从临时文件路径加载文件
            return self.load_from_file(file_path, return_text, is_unstructured)

    @classmethod
    def load_from_url(cls, url: str, return_text: bool = False) -> Union[list[Document], str]:
        """从远程URL路径加载文件为LangChain文档列表或字符串"""

        # 获取远程URL路径的文件
        response = requests.get(url)

        # 创建临时文件夹
        with tempfile.TemporaryDirectory() as temp_dir:
            # 构建临时文件路径
            file_path = os.path.join(temp_dir, os.path.basename(url))

            # 写入本地文件
            with open(file_path, "wb") as file:
                file.write(response.content)

            # 从临时文件路径加载文件
            return cls.load_from_file(file_path, return_text)

    @classmethod
    def load_from_file(
            cls,
            file_path: str,
            return_text: bool = False,
            is_unstructured: bool = True
    ) -> Union[list[Document], str]:
        """从文件路径加载文件为LangChain文档列表或字符串"""

        # 获取文件扩展名
        delimiter = "\n\n"
        file_extension = Path(file_path).suffix.lower()

        # 根据文件扩展名调用对应加载器
        if file_extension in [".md", ".markdown"]:
            loader = UnstructuredMarkdownLoader(file_path)
        elif file_extension == ".pdf":
            loader = UnstructuredPDFLoader(file_path)
        elif file_extension in [".doc", ".docx"]:
            loader = UnstructuredWordDocumentLoader(file_path)
        elif file_extension in [".xlsx", ".xls"]:
            loader = UnstructuredExcelLoader(file_path)
        elif file_extension in [".ppt", ".pptx"]:
            loader = UnstructuredPowerPointLoader(file_path)
        elif file_extension == ".csv":
            loader = UnstructuredCSVLoader(file_path)
        elif file_extension in [".htm", ".html"]:
            loader = UnstructuredHTMLLoader(file_path)
        elif file_extension == ".xml":
            loader = UnstructuredXMLLoader(file_path)
        else:
            loader = UnstructuredFileLoader(file_path) if is_unstructured else TextLoader(file_path)

        return delimiter.join([document.page_content for document in loader.load()]) if return_text else loader.load()
