#!/usr/bin/python3
"""initializing package """

from models.engine.file_storage import FileStorage
storage = FileStorage()
storage.reload()
