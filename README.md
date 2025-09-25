# Set Light HML (High/Medium/Low) - for Home Assistant

**hml_lights.py** is a python script for Home Assistant that can adjust a Light Entity's
brightness based on a High/Medium/Low (HML) value. An [input_select Helper](https://www.home-assistant.io/integrations/input_select/)
(also called a Dropdown) is used to provide the HML values, and a yaml file describes the configuration.
When HA starts up, pscript initializes hml_lights.py which will automatically create State Triggers
which watch the HML Entity state change, so no additional Automations are required.

### (1) Install pyscript
The [**pyscript**](https://hacs-pyscript.readthedocs.io/en/stable/index.html) integration
must be installed into you Home Assistant (HA) system. Recommend you use HACS for the install.

Create the folders **/config/pyscript/scripts**, then in **pyscript** create **config.yaml** with:
```
allow_all_imports: true
hass_is_global: true
```
Then, add to your **/config/configuration.yaml**
```
pyscript: !include pyscript/config.yaml
```

### (2) Download hml_lights.py

Download **hml_lights.py** to the **scripts** folder you just created. You can do this
with [github](https://github.com/EdDuran/HA-pyscript) or from a HA Terminal
```
cd /tmp
wget https://github.com/EdDuran/HA-pyscript/archive/refs/heads/main.zip
unzip main.zip
mv HA-pyscript-main/hml_lights.py /config/pyscript/scripts
```
When the **hml_lights.py** script runs for the _first time_, a default **/config/hml_lights_config.yaml**
file will be created automatically. This demo config file contains an ***HML Entity*** and ***Light Entities***
which do not exist on your system, and thereby errors are loggedd. The config file needs to be edited
(see 4 below) for your individual system.

### (3) Create an input_select Helper
Create an [input_select Helper](https://www.home-assistant.io/integrations/input_select/) for each Light to
be controlled with hml_lights. Recommend that the name of the Helper begins with ***hml_*** so that they are
easily identified, such as: ***input_select.hml_bedroom_lights*** .. and add the required values:
- off
- low
- medium
- high

### (4) Configuration File
The **/config/hml_lights_config.yaml** file contains two sections:
- **hml_data:** contains your HML Entity Helpers and a List (one-to-many) of associated Light Entities.
- **light_data:** contains your Light Entities with a map of HML keys and brightness values (in percent).

**Note:** When creating the light_data, the keyword **off** must be quoted; i.e., 'off'

### Use Cases
***Multiple Light Entities***
- The Lanai lights are operated by two distinct Light Entities (switches). Each bulb-set uses different LED bulbs with different brightness requirements.
- The two Bedroom nightstands each have a zigbee bulb. Using the HML Entity, both lights can be operated in unison, as a single device.

***Automations***
- Triggers at sunset, sets the hml_bedroom -> low
- Triggers on zigbee button, toggles hml_bedroom -> low -> off
  - Bonus: button long-press cycles low -> medium -> high -> low

### Loading hml_lights_config.yaml
The pyscript integration loads hml_lights.py when HA is started.

When making changes to the hml_lights_config.yaml file (adding or removing Entities or adjusting
brightness values) you will need to reload pyscript from: **Developer Tools -> YAML -> pyscript**

**Note:** The Home Assistant Logger buffers output, so log messages do not appear as readily as one would hope.

-----

### Sample hml_lights_config.yaml

hml_data:
- Contains a Map(of input_select HML Helpers) -> List(of Light Entities). One HML can operate multiple Lights

light_data:
- Contains a Map(of Light Entity) -> Map(off/low/medium/high) keys with brightness percentages
```
hml_data:
  input_select.hml_bedroom:    # HML Entity which will be watched for changes
    - light.left_nightstand    # List of Light Entities to Set
    - light.right_nightstand

light_data:
  light.left_nightstand:       # Light Entity to Set
    'off': 0                   # Brightness values for off, low, medium and high
    low: 10
    medium: 50
    high: 100
  light.right_nightstand:
    'off': 0
    low: 10
    medium: 50
    high: 100
```
-----

### Troublshooting

The hml_lights.py script validates the config data when the script is loaded. This ensures
that:
- the file is formatted properly,
- the HML -> Light references match,
- contains the required HML values, and
- that the HML and Light Entities exist.

Should the config file validation fail, the script writes to the HA System Log - for example:

***When the script creates the demo hml_lights_config.yaml***
```
2025-09-24 19:04:30.873 WARNING (MainThread) [custom_components.pyscript.scripts.hml_lights] Created default [/config/hml_lights_config.yaml]; please edit with your data
2025-09-24 19:04:30.893 ERROR (MainThread) [custom_components.pyscript.scripts.hml_lights] load_hml_config: Failed to Validate [/config/hml_lights_config.yaml]: The HML Entity Helper [input_select.test_hml1] does not exist
2025-09-24 19:04:30.893 ERROR (MainThread) [custom_components.pyscript.scripts.hml_lights] Failed to create State Triggers; No HML Entities found, please check [/config/hml_lights_config.yaml]
```
