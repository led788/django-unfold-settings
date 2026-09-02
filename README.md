# Django Unfold Settings

[![GitHub](https://img.shields.io/badge/github-led788%2Fdjango--unfold--settings-blue?logo=github)](https://github.com/led788/django-unfold-settings)

A reusable Django package for managing global application settings with multiple data types via the modern `django-unfold` admin interface. Features strict validation, automated cache management, and a high-performance flat JSON API.

## Features

- **Strict Type Validation:** EAV-inspired architecture with dedicated tables for each data type (`string`, `text`, `html`, `int`, `float`, `bool`, `json`, `date`, `datetime`, `file`).
- **Unfold Admin Integration:** Responsive UI using Unfold `TabularInline` components.
- **High Performance:** Optimized querying fetches all configs in exactly **1 SQL query**.
- **Automated Caching:** Built-in cache layer with dynamic TTL and instant invalidation via signals.

## Requirements

- Python >= 3.10
- Django >= 4.2
- django-unfold >= 0.20.0

## Installation

1. Install the package:
```bash
pip install django-unfold-settings
```

2. Add `unfold` and `unfold_settings` to `INSTALLED_APPS` in `settings.py`:
```python
INSTALLED_APPS = [
    "unfold",
    "unfold_settings",
    # ...
]
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Include the API routing in your core `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    path("api/settings/", include("unfold_settings.urls")),
]
```

## Cache Configuration

You can control the API cache lifetime in `settings.py`:
```python
# Cache timeout in seconds (Default: 3600 / 1 hour)
APP_SETTINGS_CACHE_TTL = 7200  

# Disable caching completely
APP_SETTINGS_CACHE_TTL = 0  
```

## API Output

The endpoint `/api/settings/settings/` returns a flat JSON dictionary:
```json
{
  "SITE_NAME": "My App",
  "MAINTENANCE_MODE": false,
  "CONFIG": {"api_key": "12345"},
  "PROJECT_LOGO": "/media/uploads/settings/LOGO/logo.png"
}
```

## License

MIT
