# Used to limit description field on all content types
DESCRIPTION_MAX_LENGTH = 700

DIRECTORY_URL = os.environ.get("DIRECTORY_URL", "https://annuaire.enwallonie.be")

# Used to translated terms from brains metadatas
# Must be extended by other products
VOCABULARIES_MAPPING = {
    "iam": "imio.smartweb.vocabulary.IAm",
    "topics": "imio.smartweb.vocabulary.Topics",
}

# Used for vocabularies that allow explicitly choosen lang translations
TRANSLATED_VOCABULARIES = [
    "imio.smartweb.vocabulary.Countries",
]

# IA service configuration (URL, application id, organization id) and
# authentication are now provided by imio.omnia.core (IOmniaCoreAPIService
# adapter + Plone registry settings), see imio.omnia.core.settings.
