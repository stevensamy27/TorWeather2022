"""
The emails module contains methods to send individual confirmation
and confirmed emails as well as methods to return tuples needed by Django's 
send_mass_mail() method.
Emails are sent after all database checks/updates. 

@type _SENDER: str
@var _SENDER: The email address for the Tor Weather emailer

@type _SUBJECT_HEADER: str
@var _SUBJECT_HEADER: The base for all email headers.

@type _CONFIRMATION_SUBJ: str
@var _CONFIRMATION_SUBJ: The subject line for the confirmation mail

@type _CONFIRMATION_MAIL: str
@var _CONFIRMATION_MAIL: The email message sent upon first subscribing.
    The email contains a link to the user-specific confirmation
    page, which the user must follow to confirm.

"""
import re

from config import url_helper
from weatherapp.models import insert_fingerprint_spaces

from django.core.mail import send_mail

_SENDER = 'tor-ops@torproject.org'
_SUBJECT_HEADER = '[Tor Weather] '

_CONFIRMATION_SUBJ = 'Confirmation Needed'
_CONFIRMATION_MAIL = "Dear human,\n\n" +\
    "This is the Tor Weather Report system.\n\n" +\
    "Someone (possibly you) has requested that status monitoring "+\
    "information about a Tor node %s be sent to this email "+\
    "address.\n\nIf you wish to confirm this request, please visit the "+\
    "following url:\n\n%s\n\nIf you do not wish to receive Tor Weather "+\
    "Reports, you don't need to do anything. You shouldn't hear from us "+\
    "again."

def _get_router_name(fingerprint, name):
    """
    Returns a string representation of the name and fingerprint of
    this router. Ex: 'WesCSTor (id: 4094 8034 ...)'
    
    @type fingerprint: str
    @param fingerprint: A router fingerprint

    @type name: str
    @param name: A router name

    """

    spaced_fingerprint = insert_fingerprint_spaces(fingerprint) 
    if name == 'Unnamed':
        return "(id: %s)" % spaced_fingerprint
    else:
        return "%s (id: %s)" % (name, spaced_fingerprint)

def send_confirmation(recipient, fingerprint, name, confirm_auth):
    """
    This method sends a confirmation email to the user. The email 
    contains a complete link to the confirmation page, which the user 
    must follow in order to subscribe.
    The Django method send_mail is
    called with fail_silently=True so that an error is not thrown if the
    mail isn't successfully delivered.
    
    @type recipient: str
    @param recipient: The user's email address

    @type fingerprint: str
    @param fingerprint: The fingerprint of the node this user wishes to
        monitor.

    @type confirm_auth: str
    @param confirm_auth: The user's unique confirmation authorization key.
    """

    router = _get_router_name(fingerprint, name)
    confirm_url = url_helper.get_confirm_url(confirm_auth)
    msg = _CONFIRMATION_MAIL % (router, confirm_url)
    sender = _SENDER
    subj = _SUBJECT_HEADER + _CONFIRMATION_SUBJ
    send_mail(subj, msg, sender, [recipient], fail_silently=True)
