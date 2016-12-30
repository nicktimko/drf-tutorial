# DRF!

Using IPython notebook instead of the shell. Install the kernel (`pip install ipykernel`) and plug it into your existing notebook setup (`python -m ipykernel install --user --name drf-toot --display-name "DRF Tutorial"`), or just install Jupyter whole-cloth (`pip install jupyter`). The below snippet should be sufficient to do the Django magic?

```
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tutorial.settings")
import django
django.setup()
```
