from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0002_remove_integrityevent'),
    ]

    operations = [
        migrations.RemoveField(model_name='answer', name='teacher_score'),
        migrations.RemoveField(model_name='answer', name='seconds'),
        migrations.RemoveField(model_name='answer', name='pasted_chars'),
    ]
