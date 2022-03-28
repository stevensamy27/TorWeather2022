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
    """
    Encoded a url by
    Returns a random, url-safe string of 24 characters (no '+' or '/'characters).
    The generated string does not end in '-'. Main purpose is
    for authorization URL extensions.
        
    @rtype: str
    @return: A randomly generated, 24 character string (url-safe).
    """
    r = base64.urlsafe_b64encode(os.urandom(18))

    # some email clients don't like URLs ending in -
    if r.endswith("-"):
        r = r.replace("-", "x")
    return r  

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
    but these fields are practically used and thought of as instance variables,
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
    '''
    Model for Tor Weather subscribers. 

    @type _EMAIL_MAX_LEN: int
    @cvar _EMAIL_MAX_LEN: Maximum length for L{email} field.

    @type _AUTH_MAX_LEN: int
    @cvar _AUTH_MAX_LEN: Maximum length for L{confirm_auth}, L{unsubs_auth}, L{pref_auth}

    @type _DEFAULTS: Dictionary
    @cvar _DEFAULTS: Dictionary mapping field names to their default parameters.
    These are the values that fields will be instantiated with if 
    they are not specified in the model's construction.

    @type email: EmailField (str)
    @ivar email: The L{Subscriber}'s email address. 
                 Required constructor argument.
    @type router: L{Router}
    @ivar router: The L{Router} the L{Subscriber} is subscribed to.
                  Required constructor argument.

    @type confirmed: BooleanField (bool)
    @ivar confirmed: Whether the user has confirmed their subscription through
        an email confirmation link; C{True} if they have, C{False} if they 
        haven't. Default value is C{False}.
    
    @type confirm_auth: CharField (str)
    @ivar confirm_auth: Confirmation authorization code. Default value is a
        random string generated by L{get_rand_string}.

    @type unsubs_auth: CharField (str)
    @ivar unsubs_auth: Unsubscription authorization code. Default value is a
        random string generated by L{get_rand_string}.

    @type pref_auth: CharField (str)
    @ivar pref_auth: Preferences access authorization code. Default value is a
        random string generated by L{get_rand_string}.


    @type sub_date: DateTimeField (datetime)
    @ivar sub_date: Datetime at which the L{Subscriber} subscribed. Default 
        value is the current time, evaluated by a call to C{datetime.now}.

    '''
    _EMAIL_MAX_LEN = 75
    _AUTH_MAX_LEN = 25
    _DEFAULTS = { 'confirmed': False,
                  'confirm_auth': get_rand_string,
                  'unsubs_auth': get_rand_string,
                  'pref_auth': get_rand_string,
                  'sub_date': datetime.now }


    email = models.EmailField(max_length=_EMAIL_MAX_LEN, default=None, blank=False)
    router = models.ForeignKey(Router, default=None,on_delete=models.CASCADE, blank=False)
    confirmed = models.BooleanField(default=_DEFAULTS['confirmed'])
    confirm_auth = models.CharField(max_length=_AUTH_MAX_LEN, default=_DEFAULTS['confirm_auth'])
    unsubs_auth = models.CharField(max_length=_AUTH_MAX_LEN, default=_DEFAULTS['unsubs_auth'])
    pref_auth = models.CharField(max_length=_AUTH_MAX_LEN, default=_DEFAULTS['pref_auth'])
    sub_date = models.DateTimeField(default=_DEFAULTS['sub_date'])


class Subscription(models.Model):

    """
    Generic (abstract) model for Tor Weather subscriptions. Only contains
    fields which are used by all types of Tor Weathe Dictionary subscriptions.

    Django uses class variables to specify model fields, but these fields are
    practically used and thought of as instance variables, so this 
    documentation will refer to them as such. Field types are specified as 
    their Django field classes, with parentheses indicating the python type 
    they are validated against and treated as practically. When constructing
    a L{Subscription} object, instance variables are specified as keyword
    arguments in L{Subscription} constructors.

    @type _DEFAULTS: dict {str: various}
    @cvar _DEFAULTS: Dictionary mapping field names to their default
        parameters. These are the values that fields will be instantiated
        with if they are not specified in the model's construction.

    @type subscriber: L{Subscriber}
    @ivar subscriber: The L{Subscriber} who is subscribed to this
        L{Subscription}. Required constructor argument.
    @type emailed: BooleanField (bool)
    @ivar emailed: Whether the user has already been emailed about this
        L{Subscription} since it has been triggered; C{True} if they have
        been, C{False} if they haven't been. Default value is C{False}.
    """

    _DEFAULTS = { 'emailed': False }

    subscriber = models.ForeignKey(Subscriber, default=None,on_delete=models.CASCADE, blank=False)
    emailed = models.BooleanField(default=_DEFAULTS['emailed'])

# SUBSCRIPTION SUBCLASSES -----------------------------------------------------
# -----------------------------------------------------------------------------


# FORMS -----------------------------------------------------------------------
# -----------------------------------------------------------------------------


# CUSTOM FIELDS ---------------------------------------------------------------
# -----------------------------------------------------------------------------


# Create your models here.


