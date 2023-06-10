from django.urls import path, include

from supporter.views import organizations

urlpatterns = [
    path("organizations/", organizations, name="organizations"),
]

app_name = "supporter"