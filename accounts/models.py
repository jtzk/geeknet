from django.db import models
from django.contrib.auth.models import User

User.add_to_class('birthday', models.DateField(blank=True, null=True))
