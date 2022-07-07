import base64
import imghdr
import uuid

from django.core.files.base import ContentFile
from rest_framework import fields


class DecodeImageField(fields.ImageField):

    def to_internal_value(self, data):
        data = data.split(';base64,')
        decoded_file = base64.b64decode(data)
        file_name = str(uuid.uuid4())[:10]
        file_extension = self.get_file_extension(file_name, decoded_file)
        complete_file_name = f'{file_name}.{file_extension}'
        data = ContentFile(decoded_file, name=complete_file_name)
        return super(DecodeImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        extension = imghdr.what(file_name, decoded_file)
        extension = 'jpg' if extension == 'jpeg' else extension
        return extension
