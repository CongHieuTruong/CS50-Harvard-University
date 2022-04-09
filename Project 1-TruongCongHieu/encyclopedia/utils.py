import re
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def save_req_entry(oldTitle, newTitle, pageContent):
    # Save file for backup if needed
    if oldTitle != None and oldTitle != newTitle:
        default_storage.delete(f"entries/{oldTitle}.md")
    file = f"entries/{newTitle}.md"
    if default_storage.exists(file):
        default_storage.delete(file)
    default_storage.save(file, ContentFile(pageContent))
