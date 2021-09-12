from __future__ import unicode_literals

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0044_auto_20180823_0452'),
    ]

    operations = [
        migrations.AlterField(
            field=models.DateTimeField(
                auto_now_add=True, db_index=True,
                help_text='The server date and time when the document was '
                'finally processed and added to the system.',
                verbose_name='Added'
            ), model_name='document', name='date_added',
        ),
        migrations.AlterField(
            field=models.DateTimeField(
                blank=True, help_text='The server date and time when the '
                'document was moved to the trash.', null=True,
                verbose_name='Date and time trashed'
            ), model_name='document', name='deleted_date_time',
        ),
        migrations.AlterField(
            field=models.TextField(
                blank=True, default='', help_text='An optional short text '
                'describing a document.', verbose_name='Description'
            ), model_name='document', name='description',
        ),
        migrations.AlterField(
            field=models.BooleanField(
                db_index=True, default=False, editable=False,
                help_text='Whether or not this document is in the trash.',
                verbose_name='In trash?'
            ), model_name='document', name='in_trash',
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, db_index=True, default='',
                help_text='The name of the document.', max_length=255,
                verbose_name='Label'
            ), model_name='document', name='label',
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, default=b'eng', help_text='The dominant '
                'language in the document.', max_length=8,
                verbose_name='Language'
            ), model_name='document', name='language',
        ),
        migrations.AlterField(
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, help_text='UUID of a '
                'document, universally Unique ID. An unique identifier '
                'generated for each document.', verbose_name='UUID'
            ), model_name='document', name='uuid',
        ),
        migrations.AlterField(
            field=models.CharField(
                help_text='The name of the document type.', max_length=32,
                unique=True, verbose_name='Label'
            ), model_name='documenttype', name='label',
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, db_index=True, editable=False,
                help_text='A hash/checkdigit/fingerprint generated from the '
                'document\'s binary data. Only identical documents will have '
                'the same checksum.', max_length=64, null=True,
                verbose_name='Checksum'
            ), model_name='documentversion', name='checksum',
        ),
        migrations.AlterField(
            field=models.TextField(
                blank=True, default='', help_text='An optional short text '
                'describing the document version.', verbose_name='Comment'
            ), model_name='documentversion', name='comment',
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, editable=False, help_text='The document version '
                'file encoding. binary 7-bit, binary 8-bit, text, base64, '
                'etc.', max_length=64, null=True, verbose_name='Encoding'
            ), model_name='documentversion', name='encoding',
        ),
        migrations.AlterField(
            field=models.CharField(
                blank=True, editable=False, help_text='The document '
                'version\'s file mimetype. MIME types are a standard way '
                'to describe the format of a file, in this case the file '
                'format of the document. Some examples: "text/plain" or '
                '"image/jpeg". ', max_length=255, null=True,
                verbose_name='MIME type'
            ), model_name='documentversion', name='mimetype',
        ),
        migrations.AlterField(
            field=models.DateTimeField(
                auto_now_add=True, db_index=True, help_text='The server '
                'date and time when the document version was processed.',
                verbose_name='Timestamp'
            ), model_name='documentversion', name='timestamp',
        ),
    ]