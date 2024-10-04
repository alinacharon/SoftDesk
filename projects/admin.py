from django.contrib import admin
from .models import Contributor, Project, Issue, Comment, User

admin.site.register(User)
admin.site.register(Contributor)
admin.site.register(Project)
admin.site.register(Issue)
admin.site.register(Comment)
