from imio.smartweb.common.config import IPA_URL
from imio.smartweb.common.config import APPLICATION_ID
from imio.smartweb.common.config import PROJECT_ID
from imio.smartweb.common.utils import get_vocabulary
from plone import api
from Products.Five import BrowserView
from zope.i18n import translate

import json
import requests


class BaseIAView(BrowserView):
    """
    Base view providing common headers and configuration for IA-related features.
    This class is shared across multiple projects, including imio.smartweb.core.
    """

    _headers = None

    @property
    def headers(self):
        if self._headers is None:
            self._headers = {
                "accept": "application/json",
                "Content-Type": "application/json",
                "x-imio-application": APPLICATION_ID,
                "x-imio-municipality": PROJECT_ID,
            }
        return self._headers

    @property
    def headers_json(self):
        return json.dumps(self.headers)


class ProcessSuggestedTitlesView(BaseIAView):

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )
        current_html = self.request.form.get("text", "")
        payload = {
            "input": current_html,
            "expansion_target": 50,
        }
        url = f"{IPA_URL}/suggest-titles"
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code != 200:
            return current_html
        data = response.json()
        if not data:
            return current_html
        return json.dumps(data)


class BaseProcessCategorizeContentView(BaseIAView):

    timeout = (5, 20)

    def __init__(self, context, request):
        super().__init__(context, request)
        self.current_lang = api.portal.get_current_language()[:2]

    def _get_structured_data_from_vocabulary(self, vocabulary_name):
        voc = get_vocabulary(vocabulary_name)
        voc_translated_dict = [
            {
                "title": translate(t.title, target_language=self.current_lang),
                "token": t.token,
            }
            for t in voc
        ]
        return voc_translated_dict

    def _ask_categorization_to_ia(self, text, voc):
        payload = {"input": text, "vocabulary": voc, "unique": False}
        url = f"{IPA_URL}/categorize-content"
        try:
            response = requests.post(
                url, headers=self.headers, json=payload, timeout=self.timeout
            )
            response.raise_for_status()
            return response.json() or {}
        except requests.RequestException:
            return {}

    def _merge_existing_tokens(self, ia_list, existing_tokens, full_voc):
        """Ajoute les tokens déjà enregistrés mais absents de la réponse IA."""
        ia_tokens = {t.get("token") for t in ia_list}
        for token in existing_tokens or []:
            if token not in ia_tokens:
                item = next((t for t in full_voc if t.get("token") == token), None)
                if item:
                    ia_list.append(item)
        return ia_list

    def _process_iam(self, all_text, results):
        iam_voc = self._get_structured_data_from_vocabulary(
            "imio.smartweb.vocabulary.IAm"
        )
        data = self._ask_categorization_to_ia(all_text, iam_voc)
        if not data:
            return
        ia_iam = [
            {"title": r.get("title"), "token": r.get("token")}
            for r in data.get("result", [])
        ]
        ia_iam = self._merge_existing_tokens(
            ia_iam, getattr(self.context, "iam", []), iam_voc
        )
        results["form-widgets-IAm-iam"] = ia_iam

    def _process_topics(self, all_text, results):
        topics_voc = self._get_structured_data_from_vocabulary(
            "imio.smartweb.vocabulary.Topics"
        )
        data = self._ask_categorization_to_ia(all_text, topics_voc)
        if not data:
            return
        ia_topics = [
            {"title": r.get("title"), "token": r.get("token")}
            for r in data.get("result", [])
        ]
        ia_topics = self._merge_existing_tokens(
            ia_topics, getattr(self.context, "topics", []), topics_voc
        )
        results["form-widgets-ITopics-topics"] = ia_topics

    def _get_all_text(self):
        """To implement in child class"""
        raise NotImplementedError("_get_all_text must be defined in subclasses")

    def _process_specific(self, all_text="", results={}):
        """To implement in child class"""
        raise NotImplementedError("_process_specific must be defined in subclasses")

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )

        all_text = self._get_all_text()
        results = {}
        self._process_iam(all_text, results)
        self._process_topics(all_text, results)
        self._process_specific(all_text, results)
        return json.dumps(
            {"ok": True, "message": "Catégorisation calculée", "data": results}
        )
