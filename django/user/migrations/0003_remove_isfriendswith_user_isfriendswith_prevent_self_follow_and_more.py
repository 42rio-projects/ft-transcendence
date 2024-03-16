# Generated by Django 5.0.2 on 2024-03-04 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_isfriendswith_user_friends_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='isfriendswith',
            name='user_isfriendswith_prevent_self_follow',
        ),
        migrations.AddConstraint(
            model_name='isfriendswith',
            constraint=models.CheckConstraint(check=models.Q(('user1', models.F('user2')), _negated=True), name='user_isfriendswith_prevent_self_add'),
        ),
    ]
