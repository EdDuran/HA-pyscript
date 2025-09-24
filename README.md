# Set Light HML (High/Medium/Low) - PyScript Version

This Home Assistant python script adjusts light brightness based on HML (High/Medium/Low)
input_select Helper values. Place this file in your **/config/pyscript/scripts** directory.

The **/config/hml_lights_config.yaml** file describes the relationship between each HML Entity
and its one-or-more Light Entities. Each Light Entity can have their own specific brightness
values (in the case of multiple lights, having different lighting brightness)

When this script is loaded, the hml_lights_config.yaml is read and triggers automatically
created .. that is, no need to create individual Automations, this script does it.

If making changes to the hml_lights_config.yaml file (adding or removing Entities or adjusting
brightness values) you simply reload pyscript from Developer Tools -> YAML

It seems the Home Assistant Logger buffers output, so log messages do not appear as
readily as one would hope.

-----

### Helper: input_select
For each Light to be controlled with hml_lights, create an "input_select" (aka dropdown) Helper
with the values:
- off
- low
- medium
- high

### Sample hml_lights_config.yaml

HML (High/Medium/Low) Configuration Data
Place this file in your Home Assistant /config directory

hml_data:
  Contains a Map(of input_select HML Helpers) -> List(of Light Entities)
  One HML can operate multiple Lights
light_data:
  Contains a Map(of Light Entity) -> Map(off/low/medium/high) keys with brightness percentages
```
hml_data:
  input_select.test_hml1:   # HML Entity which will be watched for changes
  - light.test_light1       # List of Light Entities to Set
  - light.test_light2

light_data:
  light.test_light1:        # Light Entity to Set
    'off': 0                # Brightness values for off, low, medium and high
    low: 10
    medium: 50
    high: 100
  light.test_light2:
    'off': 0
    low: 5
    medium: 60
    high: 100
```
