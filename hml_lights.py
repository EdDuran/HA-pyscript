"""
hml_lights.py
v1.2.0.0
Keith Roberts
Strebor Tech, September 2025

Set Light HML (High/Medium/Low) - PyScript Version
This script adjusts light brightness based on HML input_select Helper values.
Place this file in your pyscript/scripts directory.

The "/config/hml_lights_config.yaml" describes the relationship between each HML Entity
and its one-or-more Light Entities, each having their own specific brightness
values (in the case of multiple lights, having different lighting brightness)

When this script is loaded, the hml_lights_config.yaml is read and triggers automatically
created .. that is, no need to create individual Automations, this script does it.

If making changes to the hml_lights_config.yaml file (adding or removing Entities or adjusting
brightness values) use Developer Tools -> Actions -> pyscript.load_hml_lights_config

It seems the Home Assistant Logger buffers output, so log messages do not appear as
readily as one would hope.
"""

import aiofiles
import yaml
import os
from builtins import open  # Explicitly import open if needed

HML_CONFIG_FILE = "/config/hml_lights_config.yaml"
HML_DATA = None
LIGHT_DATA = None

class HMLConfigException(Exception):
    """HML Config Validation Exception"""
    def __init__(self, message="HML Config Validation Occurred"):
        Exception.__init__(self, message)
#
# ----- Create HML Config -----
#
def create_hml_config():
    default_config = """
# HML (High/Medium/Low) Configuration Data
# Place this file in your Home Assistant /config directory
#
# hml_data:
#   Contains a Map(of input_select HML Helpers) -> List(of Light Entities)
#   One HML could operate multiple Lights
# light_data:
#   Contains a Map(of Light Entity) -> Map(off/low/medium/high with brightness percentages
#
# *** Please edit with your own HML and Light Entities ***
#
hml_data:
  input_select.test_hml1:   # HML Entity which will be watched for changes
    - light.test_light1     # List of Light Entities to Set
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
"""
    try:
        async with aiofiles.open(HML_CONFIG_FILE, mode='w') as f:
            f.write(default_config)
        log.warning(f"Created default [{HML_CONFIG_FILE}]; please edit with your data")
    except Exception as e:
        log.error(f"Failed to create default [{HML_CONFIG_FILE}]: {e}")

#
# ----- Validate HML Config Data -----
#
def validate_config(hml_data, light_data):
    # hml_data exist?
    if (not hml_data or len(hml_data) == 0):
        raise HMLConfigException(f"The 'hml_data:' section is missing or empty")
    if not isinstance(hml_data, dict):
        raise HMLConfigException(f"The 'hml_data:' section must be a Map of HML input_select Helpers")

    # light_data exist?
    if (not light_data or len(light_data) == 0):
        raise HMLConfigException(f"The 'light_data:' section is missing or empty")

    required_keys = {'off', 'low', 'medium', 'high'}
    referenced_lights = set()

    # Verify hml_data references existing light_data
    for hml_entity, lights in hml_data.items():
        # hml_entity must exist
        if (not state.exist(hml_entity)):
            raise HMLConfigException(f"The HML Entity Helper [{hml_entity}] does not exist")

        # Each value in hml_data should be a list
        if not isinstance(lights, list):
            raise HMLConfigException(f"The 'hml_data:' for [{hml_entity}] must contain a List of Light Entities")

        # Check each light in the list
        for light_entity in lights:
            # Light Entity must exist
            light_hml_map = light_data.get(light_entity)
            if (light_hml_map is None):
                raise HMLConfigException(f"The light entity [{light_entity}] is referenced in 'hml_data' [{hml_entity}] but not defined in 'light_data'")
            # light_hml must be a dictionary
            if not isinstance(light_hml_map, dict):
                raise HMLConfigException(f"The 'light_data:' for Light Entity [{light_entity}] must be a Map.")

            # Light Entity must exist
            if (not state.exist(light_entity)):
                raise HMLConfigException(f"The Light Entity [{light_entity}] does not exist ")

            # Check for missing required keys
            missing_keys = required_keys - set(light_hml_map.keys())
            if missing_keys:
                raise HMLConfigException(f"'light_data:' for [{light_entity}] is missing the required HML keys: {list(missing_keys)}")

            # Check for Brightness values between 0 and 100 percent
            for key, brightness in light_hml_map.items():
                if (brightness < 0 or brightness > 100):
                    log.warning(f"'light_data:' for [{light_entity}.{key} brightness out of range [0 <= {brightness} <= 100]")
            
            referenced_lights.add(light_entity)

    # Warning about unreferenced lights in light_data
    all_lights = set(light_data.keys())
    unreferenced_lights = all_lights - referenced_lights
    if unreferenced_lights:
        log.warning(f"Ignoring unreferenced 'light_data': {list(unreferenced_lights)} in [{HML_CONFIG_FILE}]")
#
# ----- Load HML Config -----
#
def load_hml_config():
    """Load HML configuration and return hml_data, light_data"""
    try:
        # Does HML Config exist?                
        if not os.path.exists(HML_CONFIG_FILE):
            create_hml_config()

        # Read and parse HML Config
        # Must use async aiofiles.open to prevent blocking I/O
        async with aiofiles.open(HML_CONFIG_FILE, mode='r') as f:
            content = await f.read()
        config = yaml.safe_load(content)

        hml_data = config.get('hml_data', {})
        light_data = config.get('light_data', {})

        validate_config(hml_data, light_data)
        
        if (hml_data):
            log.info(f"Loaded [{HML_CONFIG_FILE}] with [{len(hml_data)} HML Entities] and [{len(light_data)} Light Entities]")
        else:
            log.error(f"Failed to load {HML_CONFIG_FILE}")

        return hml_data, light_data
        
    except FileNotFoundError:
        log.error(f"load_hml_config: Config not found: [{HML_CONFIG_FILE}]")
        return {}, {}
    except yaml.YAMLError as e:
        log.error(f"load_hml_config: Failed to parse Config: [{HML_CONFIG_FILE}]: {e}")
        return {}, {}
    except HMLConfigException as e:
        log.error(f"load_hml_config: Failed to Validate [{HML_CONFIG_FILE}]: {e}")
        return {}, {}
    except Exception as e:
        log.error(f"load_hml_config: Unexpected Error while Loading HML Config: {e}")
        return {}, {}

@time_trigger("startup")
def time_trigger_startup():
    """
    Home Assistant Startup - Load HML Lights Config
    """
    log.info("hml_lights: time_trigger_startup")
    _load_hml_lights_config()

@service
def load_hml_lights_config():
    """
    Reload HML Lights Config
    """
    log.info("hml_lights: Service -> load_hml_lights_config")
    _load_hml_lights_config()

#
# ----- load_hml_lights_config -----
#
# Load HML configuration at script Home Assistant Startup, and when
# invoked by a Service call.
#
def _load_hml_lights_config():
    """
    Load HML Lights Config
    """

    HML_DATA, LIGHT_DATA = load_hml_config()
    hml_entities = list(HML_DATA.keys())

    #
    # Dynamically create State Triggers for the HML Entities
    #
    if hml_entities:
        log.info(f"Created State Triggers for HML Entities: [{hml_entities}]")
        #
        # ----- State_Trigger -----
        #
        # Create the state trigger decorator for the loaded hml_entities
        # This method is called whenever one of the HML Entities value changes
        #
        @state_trigger(*hml_entities)
        def hml_state_changed(**kwargs):
            """
            Automatically called when any HML input_select Entity changes state.
            Entities are dynamically loaded from hml_lights_config.yaml at pyscript load time.
            
            Note: If you modify hml_lights_config.yaml, reload pyscript via:
            Developer Tools -> YAML -> "Pyscript python scripting"
            """

            # Get the entity that triggered - pyscript uses 'var_name'
            trigger_entity = kwargs.get('var_name')
            new_value = kwargs.get('value')
            old_value = kwargs.get('old_value')

            if trigger_entity:
                set_light_hml(hml_entity=trigger_entity)
            else:
                log.warning("Failed to determine which entity triggered the HML change")
    else:
        log.error(f"Failed to create State Triggers; No HML Entities found, please check [{HML_CONFIG_FILE}]")

#
# ----- Service: set_light_hml -----
#
@service
def set_light_hml(hml_entity=None, **kwargs):
    """
    Service to set light brightness based on HML input_select values
    
    Args:
        hml_entity: The input_select entity ID that triggered the change

    Typically this method is called automatically by the state_trigger, however, can
    be called manually for testing purposes
    """
    #log.info(f"HML Entity = [{hml_entity}]")

    # Validate input Entity
    if not hml_entity:
        log.error("set_light_hml: No hml_entity argument provided in call")
        return
    
    # Can't happen in Production, but could if Service called manually
    if (not HML_DATA):
        log.warning(f"set_light_hml: No 'hml_data' found in [{HML_CONFIG_FILE}]")
        return

    # Can't happen in Production, but could if Service called manually
    if hml_entity not in HML_DATA:
        log.warning(f"set_hml_light: HML Entity [{hml_entity}] was not found in hml_data. Check [{HML_CONFIG_FILE}]")
        return

    try:        
        # Get the current state of the HML input_select
        if (not state.exist(hml_entity)):
            log.error(f"set_hml_light: HML Entity [{hml_entity}] does not exist. Check [{HML_CONFIG_FILE}]")
            return
        
        hml_state = state.get(hml_entity)
        #log.info(f"Processing [{hml_entity}] with state [{hml_state}]")
        
        # Get the list of lights associated with this input_select
        lights = HML_DATA[hml_entity]
        
        # Process each Light Entity
        for light_entity in lights:
            if (not state.exist(light_entity)):
                log.error(f"set_hml_light: Light Entity [{light_entity}] does not exist. Check [{HML_CONFIG_FILE}]")
                return

            if light_entity not in LIGHT_DATA:
                log.warning(f"Light Entity [{light_entity}] not found in light_data. Check [{HML_CONFIG_FILE}]")
                continue

            # Get brightness percentage for this light and state
            brightness = LIGHT_DATA[light_entity].get(hml_state)
            
            if brightness is None:
                log.warning(f"set_hml_light: No brightness setting for [{light_entity}.{hml_state}]. Check [{HML_CONFIG_FILE}]")
                continue

            if (brightness < 0 or brightness > 100):
                adj_brightness = max(0, min(brightness, 100))
                log.warning(f"'light_data:' for [{light_entity}.{hml_state} brightness out of range [0 <= {brightness} <= 100], using [{adj_brightness}] instead")
                brightness = adj_brightness

            #log.info(f"set_hml_light: Setting [{light_entity}.{hml_state}] brightness to {brightness}%")
            
            # Turn on the light with the specified brightness
            # Note: brightness_pct of 0 turns the light off
            service.call(
                "light",
                "turn_on",
                entity_id=light_entity,
                brightness_pct=brightness
            )
    
    except Exception as e:
        log.error(f"set_light_hml: Unexpected error: {e}")
