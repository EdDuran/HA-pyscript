# Set Light HML (High/Medium/Low) - for Home Assistant

**hml_lights.py** is a python script for Home Assistant that can adjust a Light Entity
brightness based on a High/Medium/Low (HML) value. An *input_select Helper* (also called
a Dropdown) is used to provide the HML values, and a yaml file describes the configuration.
The script automatically creates State Triggers which watch the HML Entity, so no additional
Automations are required.

### (1) Install pyscript
The [**pyscript**](https://hacs-pyscript.readthedocs.io/en/stable/index.html) integration
must be installed into you Home Assistant (HA) system. Recommend you use HACS for the install.

Create the folders **/config/pyscript/scripts**, then in **pyscript** create **config.yaml** with:
```
allow_all_imports: true
hass_is_global: true
```
Finally, add to your **configuration.yaml**
```
pyscript: !include pyscript/config.yaml
```

### (2) Download hml_lights.py

Download **hml_lights.py** to the **scripts** you just created folder. You can do this
with [github](https://github.com/EdDuran/HA-pyscript) or from a HA Terminal
```
cd /tmp
wget https://github.com/EdDuran/HA-pyscript/archive/refs/heads/main.zip
unzip main.zip
mv HA-pyscript-main/hml_lights.py /config/pyscript/scripts
```
When the hml_lights.py script runs, it will automatically create a default **/config/hml_lights_config.yaml** file.
The default config file will contain an HML Entity and Light Entities which do not exist, and therefore
log errors. You'll need to edit this config file (see below) for you individual system.

### (3) Create an input_select Helper
For each Light to be controlled with hml_lights, create an "input_select" Helper.
Recommend the name of the helper begin with ***hml_*** so they are easily identified
such as: ***input_select.hml_bedroom_lights*** .. add the required values:
- off
- low
- medium
- high

### (4) Configuration File
The **/config/hml_lights_config.yaml** file contains the names of your HML Entity Helpers and one-to-many
Light Entities for which to set the brightness. Each Light Entity has their brightness values
(in the case of multiple lights, having different lighting requirements). One use case for the one-to-many
Lights is two zigbee

Place this file in your **/config/pyscript/scripts** directory.

When this script is loaded, the hml_lights_config.yaml is read and triggers automatically
created .. that is, no need to create individual Automations, this script does it.

If making changes to the hml_lights_config.yaml file (adding or removing Entities or adjusting
brightness values) you simply reload pyscript from Developer Tools -> YAML

It seems the Home Assistant Logger buffers output, so log messages do not appear as
readily as one would hope.

-----



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
