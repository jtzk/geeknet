from django.db import models
from django.contrib.auth.models import User

User.add_to_class('birthday', models.DateField(default="2200-01-01"))
