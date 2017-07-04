import voluptuous as vol
import homeassistant.helpers.config_validation as cv
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_time_change

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'person'

CONF_FIRSTNAME = 'firstname'
CONF_LASTNAME = 'lastname'
CONF_GENDER = 'gender'
CONF_DEVICE_TRACKERS = 'device_trackers'
CONF_RELATIONSHIPS = 'relationships'
CONF_RELATIONSHIPS_PERSON = 'person'
CONF_RELATIONSHIPS_RELATION = 'relation'

DEFAULT_GENDER = 'undefined'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(cv.ensure_list, [{
        vol.Required(CONF_FIRSTNAME): cv.string,
        vol.Required(CONF_LASTNAME): cv.string,
        vol.Optional(CONF_GENDER, default=DEFAULT_GENDER): cv.string,
        vol.Optional(CONF_DEVICE_TRACKERS):
            vol.All(cv.ensure_list, [
                vol.Required(cv.entity_id)
            ]),
        vol.Optional(CONF_RELATIONSHIPS):
            vol.All(cv.ensure_list, [{
                vol.Required(CONF_RELATIONSHIPS_PERSON): cv.string,
                vol.Required(CONF_RELATIONSHIPS_RELATION): cv.string,
            }])
    }])
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    persons = []
    for person_data in config.get(DOMAIN):
        person = Person(hass, person_data.get(CONF_FIRSTNAME), person_data.get(CONF_LASTNAME))
        person.gender = person_data.get(CONF_GENDER)
        owning_device_trackers = person_data.get(CONF_DEVICE_TRACKERS)
        if owning_device_trackers:
            for owning_device_tracker in owning_device_trackers:
                if owning_device_tracker in hass.states.entity_ids('device_tracker'):
                    logging.warning('Successfully added %s as a device_tracker for %s' % (owning_device_tracker, person.firstname))
                    person.add_device_tracker(hass.states.get(owning_device_tracker))

        if person_data.get(CONF_RELATIONSHIPS):
            logging.warning(person_data.get(CONF_RELATIONSHIPS))
        persons.append(person)

    for person in persons:
        hass.states.set('%s_%s.firstname' % (person.firstname, person.lastname), person.firstname)
        hass.states.set('%s_%s.lastname' % (person.firstname, person.lastname), person.lastname)
        hass.states.set('%s_%s.gender' % (person.firstname, person.lastname), person.gender)
        for device_tracker in person.device_trackers:
            logging.warning(device_tracker)
            device_name = str(device_tracker.object_id)
            logging.warning(type(device_name))
            hass.states.set('%s_%s.tracker_%s' % (person.firstname, person.lastname, device_name), device_tracker.state)

    return True


class Person(Entity):
    """
    Person and possibly something we could use as an user.
    """

    RELATIONSHIPS_STATES = dict(
        CHILD={
            'opposite': 'PARENT'
        },
        PARENT={
            'opposite': 'CHILD'
        },
        PARTNER={
            'opposite': 'PARTNER'
        },
        WIFE={
            'opposite': 'HUSBAND'
        },
        HUSBAND={
            'opposite': 'WIFE'
        }
    )

    def __init__(self, hass, firstname, lastname):
        """
        :param firstname: 
        :param lastname: 
        """
        self._hass = hass
        self._firstname = firstname
        self._lastname = lastname
        self._relationships = []
        self._device_trackers = []
        self._gender = None

        # Run update every 5 seconds.
        track_time_change(hass, lambda now: self.update(), second=range(0, 60, 5))

    @property
    def firstname(self):
        return self._firstname

    @property
    def lastname(self):
        return self._lastname

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, gender):
        """
        :param gender: The good ol' gender question.... Binary?  
        :return: 
        """
        self._gender = gender

    @property
    def device_trackers(self):
        return self._device_trackers

    def add_device_tracker(self, device_tracker):
        self._device_trackers.append(device_tracker)

    @property
    def relationships(self):
        return self._relationships

    def add_relationship(self, person, type):
        self._relationships.append({person: person, type: type})

    def update(self):
        logging.warning('Shit is updating, yoh')
