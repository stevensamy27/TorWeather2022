'''

The models module handles the bulk of Tor Weather's database management. 
The module contains three models that correspond to the three main database tables
    L{Router}, 
    L{Subscriber}, 
    L{Subscription}),
as well as four subclasses of L{Subscription} for the various subscription types and 
three classes for forms
    L{GenericForm}, 
    L{SubscribeForm},
    L{PreferencesForm}),
which specify and do the work of the forms displayed on the sign-up and preferences pages.
------------------------------------------------------------
@group Helper Functions:
    insert_fingerprint_spaces, 
    get_rand_string,
    hours_since
------------------------------------------------------------
@group Models:
    Router, 
    Subscriber, 
    Subscription
------------------------------------------------------------
@group Subscription Subclasses: 
    NodeDownSub,
    VersionSub,
    BandwidthSub, 
    TShirtSub
------------------------------------------------------------
@group Forms:
    GenericForm,
    SubscribeForm, 
    PreferencesForm
    
------------------------------------------------------------
@group Custom Fields: PrefixedIntegerField

'''
from datetime import datetime
import base64
from msilib.schema import Class
import os
import re
from copy import copy
from unicodedata import name

from config import url_helper

from django.db import models
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models


# HELPER FUNCTIONS ------------------------------------------------------------
# ----------------------------------------------------------------------------- 
def insert_fingerprint_spaces(fingerprint):
    """
    Insert a space into C{fingerprint} every four characters.

    @type fingerprint: str
    @arg fingerprint: A router L{fingerprint<Router.fingerprint>}

    @rtype: str
    @return: a L{fingerprint<Router.fingerprint>} with spaces inserted every 
    four characters.
    """
    return ' '.join(re.findall('.{4}', str(fingerprint)))    

def get_rand_string():

    pass

def hours_since(time):
    """
    Get the number of hours passed since datetime C{time}.

    @type time: C{datetime}
    @arg time: A C{datetime} object.
    @rtype: int
    @return: The number of hours since C{time}.
    """

    delta = datetime.now() - time
    hours = (delta.day * 24) + (delta.seconds / 3600)
    return hours 
    

# MODELS ----------------------------------------------------------------------
# -----------------------------------------------------------------------------

class Router(models.Model):
    '''
    Model for Tor network routers.

    Django uses class variables to specify model fields, 
    but these fields arepractically used and thought of as instance variables,
    so this documentation will refer to them as such.

    Field types are specified as their Django field classes, 
    with parentheses indicating the python type they are validated against and are treated as practically.

    When constructing a L{Router} object, instance variables are specified as 
    keyword arguments in L{Router} constructors.

    @type _FINGERPRINT_MAX_LEN: int
    @cvar _FINGERPRINT_MAX_LEN: Maximum valid length for L{fingerprint} fields.

    @type _NAME_MAX_LEN: int
    @cvar _NAME_MAX_LEN: Maximum valid length for L{name} fields.

    @type _DEFAULTS: dict {str: various}
    @cvar _DEFAULTS: Dictionary mapping field names to their default parameters.

    These are the values that fields will be instantiated with if they are not specified in the model's construction.

    @type fingerprint: CharField (str)
    @ivar fingerprint: The L{Router}'s fingerprint. Required constructor argument.

    @type name: CharField (str)
    @ivar name: The L{Router}'s name. Default value is C{'Unnamed'}.
    
    @type welcomed: BooleanField (bool)
    @ivar welcomed: Whether the L{Router} operator has received a welcome email.
    Default value is C{False}.

    @type up: BooleanField (bool)
    @ivar up: Whether this L{Router} was up the last time a new consensus document was published. 
    Default value is C{True}.

    @type exit: BooleanField (bool)
    @ivar exit: Whether this L{Router} is an exit node (if it accepts exits to port 80).
    Default is C{False}.
    '''
    _FINGERPRINT_MAX_LEN = 40
    _NAME_MAX_LEN = 100
    _DEFAULTS = { 'name': 'Unnamed',
                  'welcomed': False,
                  'last_seen': datetime.now,
                  'up': True,
                  'exit': False 
                }

    fingerprint = models.CharField(max_length=_FINGERPRINT_MAX_LEN, default=None, blank=False)

    name = models.CharField(max_length=_NAME_MAX_LEN, default=_DEFAULTS['name'])

    last_seen = models.DateTimeField(default=_DEFAULTS['last_seen'])

    welcomed = models.BooleanField(default=_DEFAULTS['welcomed'])
    up = models.BooleanField(default=_DEFAULTS['up'])
    exit = models.BooleanField(default=_DEFAULTS['exit'])

    def __unicode__(self):
        """
        Returns a simple description of this L{Router}, namely its L{name}
        and L{fingerprint}.
        
        @rtype: str
        @return: Simple description of L{Router} object.
        """
        return self.name + ": " + self.spaced_fingerprint()

    def spaced_fingerprint(self):
        """
        Returns the L{fingerprint} for this L{Router} as a string with
        spaces inserted every 4 characters.
        
        @rtype: str
        @return: The L{Router}'s L{fingerprint} with spaces inserted.
        """
        return insert_fingerprint_spaces(self.fingerprint)



class Subscriber(models.Model):
    pass


class Subscription(models.Model):
    pass

# SUBSCRIPTION SUBCLASSES -----------------------------------------------------
# -----------------------------------------------------------------------------


# FORMS -----------------------------------------------------------------------
# -----------------------------------------------------------------------------


# CUSTOM FIELDS ---------------------------------------------------------------
# -----------------------------------------------------------------------------


# Create your models here.


