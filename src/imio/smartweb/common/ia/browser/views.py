from imio.omnia.core.interfaces import IOmniaCoreAPIService
from imio.smartweb.common.utils import get_vocabulary
from plone import api
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from zope.i18n import translate

import json


class BaseIAView(BrowserView):
    """
    Base view for IA-related features.

    The IA service (URL + authentication headers) is provided by
    imio.omnia.core through the ``IOmniaCoreAPIService`` adapter.
    This class is shared across multiple projects, including imio.smartweb.core.
    """

    @property
    def ia_service(self):
        return getMultiAdapter((self.context, self.request), IOmniaCoreAPIService)


class ProcessSuggestedTitlesView(BaseIAView):

    def __call__(self):
        self.request.response.setHeader(
            "Content-Type", "application/json; charset=utf-8"
        )
        current_html = self.request.form.get("text", "")
        try:
            data = self.ia_service.suggest_titles(current_html)
        except Exception:
            return current_html
        if not data:
            return current_html
        return json.dumps(data)


class BaseProcessCategorizeContentView(BaseIAView):

    def __init__(self, context, request):
        super().__init__(context, request)
        self.current_lang = api.portal.get_current_language()[:2]

    def _get_structured_data_from_vocabulary(self, vocabulary_name, obj=None):
        voc = get_vocabulary(vocabulary_name, obj)
        voc_translated_dict = [
            {
                "title": translate(t.title, target_language=self.current_lang),
                "token": t.token,
            }
            for t in voc
        ]
        return voc_translated_dict

    def _ask_categorization_to_ia(self, text, voc):
        try:
            data = self.ia_service.categorize_content(text, voc, unique=False)
            return data or {}
        except Exception:
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
