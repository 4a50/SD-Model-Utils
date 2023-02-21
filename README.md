# Stable Diffusion Sample and Model Cycler
## By: [4a50](https://github.com/4a50)
---
### Python Script to take a Stable Diffusion Image and cycle through either all Samplers, all Models, or both

**Requires**: [Stable Diffusion Web UI by AUTOMATIC1111](https://github.com/AUTOMATIC1111/stable-diffusion-webui/) running in API mode.

---
Command Line:
```
usage: SD-images-Script.py [-h] [-ma] [-sa] [-ss] [-ms] path

Cycles a supplied image through all/selected Models and Samplers

positional arguments:
  path                  Path to PNG file with Stable Diffusion data

options:
  -h, --help            show this help message and exit
  -ma, --modelsall      Use All Models
  -sa, --samplersall    Use All Samplers
  -ss, --samplerselect  Use Only Selected Samplers
  -ms, --modelsselect   Use Only Selected Models

No options provided will create an image using data from image
```

|Version|Description|Date
|---|---|--|
|1.0| Use PNG to cycle through Samplers or Models CLI|2/20/21
|1.1| Added Selectable Models and Samplers|2/21/21