__author__ = 'Owner'

from django.db.models import Q
from django.contrib.auth.models import User

class IssueSearch(object):
    def __init__(self, search_data):
        self.__dict__.update(search_data)

    def search_title(self, q):
        if self.title:
            words = self.title.split()
            title_q = Q()
            for word in words:
                title_q = title_q | Q(title__icontains=word) | Q(owner__username__icontains=word) | Q(owner__first_name__icontains=word) | Q(owner__last_name__icontains=word)
            keyword_q = title_q
            q = q & keyword_q
            print q

        return q

    def search_created(self, q):
        if self.created:
            q = q & Q(created__icontains=self.created)
        return q

    def search_owner(self, q):
        if self.owner:
            q = q & Q(owner_id__username__icontains=self.owner)
        return q