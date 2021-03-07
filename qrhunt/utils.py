import math
import os
import uuid

from django.db.models import FileField, CharField
from django.forms import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


def check_matric(matric):
    if len(matric) != 9:
        raise forms.ValidationError(_('Matric number should be 8 characters long.'))

    try:
        matric_type = matric[0]
        year = int(matric[1:3])
        num = int(matric[1:8])
    except Exception:
        raise forms.ValidationError(_('Wrong matric number format, please double check.'))

    results = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "J",
            "K",
            "L",
            "ERROR",
    ]

    a_sum = 0

    if matric_type == "U":
        if year >= 17:
            weight = [6, 7, 4, 3, 8, 9, 2]
            offset = 4
        else:
            weight = [10, 7, 4, 3, 2, 9, 8]
            offset = 0
    elif matric_type == "B":
        weight = [10, 7, 4, 3, 2, 9, 8]
        offset = 9
    else:
        raise forms.ValidationError(_('Matric number should start with U or B'))

    for i in range(1, 8):
        a_sum += (num % 10) * weight[7 - i]
        num = math.floor(num / 10)

    a_sum += offset
    remainder = a_sum % 11

    result = results[remainder]

    if matric[8] == result:
        return True
    else:
        return False


class MatriculationField(CharField):
    def __init__(self, *args, **kwargs):
        super(MatriculationField, self).__init__(*args, **kwargs)

    # def pre_save(self, model_instance, add):
    #     value = getattr(model_instance, self.attname, None)
    #     if value:
    #         value = value.upper().strip()
    #
    #         setattr(model_instance, self.attname, value)
    #         return value
    #     else:
    #         return super(MatriculationField, self).pre_save(model_instance, add)

    def clean(self, *args, **kwargs):
        data = super(MatriculationField, self).clean(*args, **kwargs)

        matric = data.upper().strip()

        try:
            check = check_matric(matric)
        except Exception:
            raise forms.ValidationError(_('Wrong matric number format, please double check.'))

        if not check:
            raise forms.ValidationError(_('Invalid matric number, please double check.'))

        return data


class ContentTypeRestrictedFileField(FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            2.5MB - 2621440
            5MB - 5242880
            10MB - 10485760
            20MB - 20971520
            50MB - 5242880
            100MB - 104857600
            250MB - 214958080
            500MB - 429916160
    """

    def __init__(self, *args, **kwargs):
        self.content_types = kwargs.pop("content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 0)

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (
                        filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass

        return data


def update_filename(instance, filename):
    path = "submissions/"
    file_format = uuid.uuid4().hex + "." + filename.split('.')[-1]
    return os.path.join(path, file_format)