from django.urls import path, include

from supporter.views import organizations, generate_and_display_message

urlpatterns = [
    path("organizations/", organizations, name="organizations"),
    path('generate_message/<str:company_name>/<str:specialization>/', generate_and_display_message, name='generate_message'),
]

app_name = "supporter"