# Bouton « Enregistrer et publier »

Date : 2026-08-07
Paquet : `imio.smartweb.common`

## Objectif

Les formulaires d'ajout et d'édition Dexterity offrent « Enregistrer » et « Annuler ».
Ajouter un troisième bouton « Enregistrer et publier » qui enregistre la saisie puis fait
passer le contenu à l'état `published`, activable type par type via un behavior.

## Décisions

| Point | Choix | Motif |
| --- | --- | --- |
| Activation | Behavior opt-in `imio.smartweb.save_and_publish` | Idiome Plone, contrôle par type |
| Portée | Formulaire d'édition **et** d'ajout | Publier dès la création est le cas fréquent |
| Cible | Transition menant à l'état `published`, en **une** étape | Cible l'état, pas un id ; n'enchaîne pas une soumission derrière « Publier » |
| Mécanisme | Publication directe dans le handler du bouton | Pas de subscriber : un `IObjectModifiedEvent` se déclenche aussi sur « Enregistrer » |

## Architecture

Deux fichiers de production modifiés ou créés. Aucun template, aucune vue nouvelle :
`CustomAddForm` / `CustomEditForm` sont déjà enregistrés pour tout contenu Dexterity sur
`IImioSmartwebCommonLayer`, le bouton s'y greffe.

### `behaviors/publish.py` (nouveau)

```python
class ISaveAndPublish(Interface):
    """Marker behavior: adds a "Save and publish" button on add/edit forms."""


def publish_transition(obj):
    """Id of the transition available to the current user leading to 'published'."""


def type_can_publish(portal_type):
    """True if portal_type has the behavior and a workflow with a 'published' state."""


def publish(obj, transition):
    """Apply transition on obj, warning the user instead of failing."""
```

`publish_transition` croise `portal_workflow.getTransitionsFor(obj)` — déjà filtré par les
guards de workflow, donc par les permissions de l'utilisateur courant — avec
`transition.new_state_id == "published"`. Il renvoie `None` si l'objet n'a pas le behavior,
est déjà publié, n'a pas de workflow, ou si l'utilisateur n'a pas la permission. Ce même
`None` pilote la visibilité du bouton **et** garantit qu'aucune transition interdite n'est
appelée.

`type_can_publish` sert au formulaire d'ajout, où l'objet n'existe pas encore : il lit les
behaviors sur la FTI du `portal_type` et vérifie que sa chaîne de workflow possède un état
`published`. Les permissions ne sont pas vérifiables à ce stade ; l'échec éventuel est
rattrapé par le handler.

### `behaviors/configure.zcml`

```xml
<plone:behavior
    name="imio.smartweb.save_and_publish"
    title="Save and publish"
    description="Add a 'Save and publish' button on add and edit forms."
    provides=".publish.ISaveAndPublish"
    />
```

Sans `factory`, ZCML utilise l'interface `provides` comme marqueur : `ISaveAndPublish.providedBy(obj)`
fonctionne via `FTIAwareSpecification` de Dexterity.

### `browser/forms.py`

Sur les deux formulaires, idiome z3c.form obligatoire pour ne pas écraser les boutons hérités :

```python
buttons = DefaultEditForm.buttons.copy()
handlers = DefaultEditForm.handlers.copy()
```

`button.buttonAndHandler` écrit dans les locals du corps de classe via
`f_locals.setdefault("buttons", Buttons())`. Sans ces deux lignes, l'attribut `buttons` de la
sous-classe ne contiendrait que le nouveau bouton et masquerait Enregistrer/Annuler.

Édition — le formulaire expose une propriété `publish_transition` qui délègue à la fonction
module du même nom, afin que la condition et le handler partagent le même calcul :

```python
@property
def publish_transition(self):
    return publish_transition(self.context)

@button.buttonAndHandler(_("Save and publish"), name="save_and_publish",
                         condition=lambda form: form.publish_transition is not None)
def handleSaveAndPublish(self, action):
    self.handleApply(action)
    if self.status == self.formErrorsMessage:
        return
    publish(self.context, self.publish_transition)
```

`publish(obj, transition)` est la troisième fonction de `behaviors/publish.py` : elle appelle
`api.content.transition` et rattrape l'échec (voir « Gestion d'erreur »).

`handleApply` reste une méthode ordinaire (le décorateur `buttonAndHandler` renvoie la
fonction d'origine), donc l'appel réutilise l'enregistrement standard : message de statut,
redirection, `EditFinishedEvent`.

Ajout : la condition s'appuie sur `type_can_publish(self.portal_type)`. Le handler rejoue
`extractData()` puis `createAndAdd(data)` et publie l'objet créé. `createAndAdd` renvoie
l'objet **avant** insertion, non enveloppé par l'acquisition ; `add()` est donc surchargé en
deux lignes pour conserver une référence à l'objet réellement placé dans le conteneur.

### Gestion d'erreur

L'appel à `api.content.transition` est enveloppé dans un `try/except WorkflowException`. En cas
d'échec, le contenu reste enregistré et un message de statut `warning` l'indique : la saisie
n'est jamais perdue.

### Ordre des boutons

Enregistrer · Annuler · Enregistrer et publier (le nouveau bouton est ajouté en fin de liste).

## Périmètre

Ce paquet **définit** le behavior ; il ne l'active sur aucun type réel. L'activer sur les types
de contenu relève d'un changement séparé dans `imio.smartweb.core`. Seul le profil `testing`
de ce paquet l'active, sur `Document`, pour les tests.

## Traduction

Le msgid `Save and publish` doit être ajouté dans `imio.smartweb.locales` (domaine
`imio.smartweb`), paquet distinct. En attendant, le libellé anglais s'affiche.

## Tests

`tests/test_save_and_publish.py`, couverture minimale 90 % :

- bouton présent sur un `Document` privé avec le behavior actif ;
- bouton absent sur un type sans le behavior (`Folder`) ;
- bouton absent sur un contenu déjà publié ;
- le bouton publie effectivement, depuis le formulaire d'édition ;
- le bouton crée puis publie, depuis le formulaire d'ajout.
