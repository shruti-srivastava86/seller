import os
import uuid


def chat_photo(instance, filename):
    extension = os.path.splitext(str(filename))[1]
    filename = str(uuid.uuid4()) + extension
    return 'chat/' + filename
