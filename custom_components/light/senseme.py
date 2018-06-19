"""
Support for Haiku with SenseME ceiling fan.

For more details about this platform, please refer to the documentation
?????
"""
import logging

from homeassistant.components.light import (Light, ATTR_BRIGHTNESS,
                                            SUPPORT_BRIGHTNESS)

from custom_components.senseme import (DATA_HUBS)

_LOGGER = logging.getLogger(__name__)

SENSEME_LIGHT_BRIGHTNESS = 'LIGHT;LEVEL;ACTUAL'
SENSEME_LIGHT_POWER  = 'LIGHT;PWR'
SENSEME_LIGHT_PRESENT = 'DEVICE;LIGHT'



def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Set up the Haiku with SenseME ceiling fan light platform."""
    lights = []
    for hub in hass.data[DATA_HUBS]:
        # add the light only if one is installed in the fan
        if hub.get_attribute(SENSEME_LIGHT_PRESENT) == 'PRESENT':
            lights.append(HaikuSenseMeLight(hass, hub))
    add_devices_callback(lights)


class HaikuSenseMeLight(Light):
    """Representation of a Haiku with SenseME ceiling fan light."""
    def __init__(self, hass, hub):
        """Initialize the entity."""
        self.hass = hass
        self._hub = hub
        self._name = hub.name + " Light"
        self._last_brightness = None
        self._supported_features = SUPPORT_BRIGHTNESS
        # _LOGGER.debug("SenseME Light: Added light '%s'." % self._name)


    @property
    def name(self):
        """Get light name."""
        return self._name


    @property
    def should_poll(self) -> bool:
        """Polling needed for this light."""
        return True


    @property
    def brightness(self) -> int:
        """Return the brightness of the light."""
        fan_brightness = int(self._hub.get_attribute(SENSEME_LIGHT_BRIGHTNESS))
        brightness = fan_brightness * 16
        if brightness > 255:
            brightness = 255
        # _LOGGER.debug("%s: Brightness:%s" % (self._name, brightness))
        return brightness


    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        state = self._hub.get_attribute(SENSEME_LIGHT_POWER) == 'ON'
        # _LOGGER.debug("%s: Is on:%s" % (self._name, state))
        return state


    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return self._supported_features


    def turn_on(self, **kwargs) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        if brightness == None:
            # brightness undefined, use last brightness if available
            if self._last_brightness:
                brightness = self._last_brightness
            else:
                brightness = 16
        else:
            if brightness >= 255:
                brightness = 16
            else:
                brightness = int(brightness / 16)
        self._hub.brightness = brightness
        # _LOGGER.debug("%s: Turn light on. Brightness: %d->%d" %
        #     (self._name, kwargs.get(ATTR_BRIGHTNESS, 255), brightness))


    def turn_off(self, **kwargs) -> None:
        """Turn off the light."""
        # use to default brightness when turning on again
        self._last_brightness = self._hub.brightness
        self._hub.light_powered_on = False
        # _LOGGER.debug("%s: Turn light off." % self._name)
