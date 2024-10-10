from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_nested import routers as nested_routers
from projects.views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

schema_view = get_schema_view(
    openapi.Info(
        title="SoftDesk API",
        default_version='v1',
        description="API for SoftDesk project",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


router = routers.SimpleRouter()
router.register(r'projects', ProjectViewSet, basename='projects')

# For issues in projects
projects_router = nested_routers.NestedSimpleRouter(
    router, r'projects', lookup='project')
projects_router.register(r'issues', IssueViewSet, basename='project-issues')

# For comments in issues
issues_router = nested_routers.NestedSimpleRouter(
    projects_router, r'issues', lookup='issue')
issues_router.register(r'comments', CommentViewSet, basename='issue-comments')

# For contributors in projects
projects_router.register(
    r'contributors', ContributorViewSet, basename='project-contributors')

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/v1/', include(projects_router.urls)),
    path('api/v1/', include(issues_router.urls)),
    path('api/v1/register/', UserRegistrationView.as_view(), name='register'),
    path('api/v1/profile/', UserProfileView.as_view(), name='profile'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
