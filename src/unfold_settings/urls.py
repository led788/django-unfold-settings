from django.urls import path
from .views import SettingsView

app_name = 'unfold_settings'

urlpatterns = [
    path('settings/', SettingsView.as_view(), name='settings-view'),
]
