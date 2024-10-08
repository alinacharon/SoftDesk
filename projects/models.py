from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    age = models.PositiveIntegerField(default=18)
    can_be_contacted = models.BooleanField(default=False)
    can_data_be_shared = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Project(models.Model):
    name = models.CharField(max_length=50, default='Project')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    contributors = models.ManyToManyField(
        User, related_name='project_contributor')
    description = models.TextField(max_length=1200)
    TYPE_CHOICES = [
        ('back-end', 'Back-End'),
        ('front-end', 'Front-End'),
        ('iOS', 'iOS'),
        ('Android', 'Android')
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Save project
        super(Project, self).save(*args, **kwargs)

        # Add autor to contributors
        if not self.contributors.filter(pk=self.author.pk).exists():
            self.contributors.add(self.author)

    def __str__(self):
        return f'{self.name} - {self.description[:50]}'


class Issue(models.Model):
    name = models.CharField(max_length=50, default='Issue')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='authored_issues')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='issues')
    assigned_users = models.ManyToManyField(
        User, related_name='assigned_issues', blank=True)

    TYPE_CHOICES = [
        ('BUG', 'Bug'),
        ('FEATURE', 'Feature'),
        ('TASK', 'Task')
    ]
    LEVEL_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High')
    ]
    STATUS_CHOICES = [
        ('ToDo', 'To Do'),
        ('InProgress', 'In Progress'),
        ('Finished', 'Finished')
    ]
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    status = models.CharField(
        max_length=50, choices=STATUS_CHOICES, default='ToDo')
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name} : {self.type} - {self.level}'


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(max_length=1200)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Issue name: {self.issue.name} - {self.description[:30]}'
