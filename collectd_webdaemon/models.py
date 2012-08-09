from django.db import models
from django.contrib.auth.models import User


class OverviewCharts(models.Model):
    """
    This model will store the list of charts specified user wants to see on
    their overview page.
    """
    user = models.ForeignKey(User, primary_key=True)
    charts = models.TextField()
