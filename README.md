# Stable Diffusion Sample and Model Cycler
## Author: JP Jones
---
### Python Script to take a Stable Diffusion Image and cycle through either all Samplers, all Models, or both

**Requires**: [Stable Diffusion Web UI by AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui/) running in API mode.

---
Command Line:
```
usage: SD-images-Script.py [-h] [-m] [-s] path

positional arguments:
  path            Path to PNG file with Stable Diffusion data

options:
  -h, --help      show this help message and exit
  -m, --models    Use All Models
  -s, --samplers  Use All Samplers
```

