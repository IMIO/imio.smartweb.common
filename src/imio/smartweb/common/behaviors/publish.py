# -*- coding: utf-8 -*-

from AccessControl import getSecurityManager
from imio.smartweb.locales import SmartwebMessageFactory as _
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.statusmessages.interfaces import IStatusMessage
from zope.component import queryUtility
from zope.interface import Interface

BEHAVIOR = "imio.smartweb.save_and_publish"
PUBLISHED = "published"


class ISaveAndPublish(Interface):
    """Marker behavior adding a "Save and publish" button on add/edit forms."""


def publish_transition(obj):
    """Transition available to the current user leading to the published state.

    Returns None when obj has not the behavior, has no workflow, is already
    published, or when the current user may not publish it: getTransitionsFor
    is already filtered by the workflow guards.
    """
    if not ISaveAndPublish.providedBy(obj):
        return None
    wf_tool = api.portal.get_tool("portal_workflow")
    for info in wf_tool.getTransitionsFor(obj):
        for workflow in wf_tool.getWorkflowsFor(obj):
            transition = workflow.transitions.get(info["id"])
            if transition is not None and transition.new_state_id == PUBLISHED:
                return info["id"]
    return None


def type_can_publish(portal_type, container):
    """Whether the current user may create portal_type in container and publish it.

    Used by the add form, where the content does not exist yet and its guards
    cannot be evaluated: the transition leading to the published state is looked
    up from the initial state of the workflow, and its guard is checked against
    container, from which the new content will acquire its permissions.
    """
    fti = queryUtility(IDexterityFTI, name=portal_type)
    if fti is None or BEHAVIOR not in fti.behaviors:
        return False
    security_manager = getSecurityManager()
    wf_tool = api.portal.get_tool("portal_workflow")
    for wf_id in wf_tool.getChainForPortalType(portal_type):
        workflow = wf_tool[wf_id]
        initial_state = workflow.states.get(workflow.initial_state)
        if initial_state is None:
            continue
        for transition_id in initial_state.transitions:
            transition = workflow.transitions.get(transition_id)
            if transition is None or transition.new_state_id != PUBLISHED:
                continue
            if transition.getGuard().check(security_manager, workflow, container):
                return True
    return False


def publish(obj, transition, request):
    """Apply transition on obj, warning the user rather than losing its input."""
    if transition is None:
        # The button was not offered to this user: nothing to publish, nothing
        # to report either.
        return
    try:
        api.content.transition(obj=obj, transition=transition)
    except (WorkflowException, api.exc.InvalidParameterError):
        IStatusMessage(request).addStatusMessage(
            _("Content saved but could not be published."), "warning"
        )
