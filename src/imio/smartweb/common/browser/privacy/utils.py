# -*- coding: utf-8 -*-


def get_all_consent_reasons(privacy_tool):
    for reason in privacy_tool.getAllReasons().values():
        if reason.lawful_basis.__name__ == "consent":
            yield reason
