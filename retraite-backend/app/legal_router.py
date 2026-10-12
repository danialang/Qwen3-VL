"""Pages publiques exigées par les boutiques d'applications : politique de confidentialité et suppression de compte.

Les liens à donner au Play Store / à l'App Store sont :
  https://VOTRE-SERVEUR/privacy             (politique de confidentialité)
  https://VOTRE-SERVEUR/account-deletion    (comment supprimer son compte et ses données)
"""
import html

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from .config import settings

router = APIRouter(tags=["legal"])

UPDATED = "octobre 2026"

PAGE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:Arial,sans-serif;background:#f3f4f6;margin:0;padding:16px;color:#1f2937;line-height:1.55}}
main{{max-width:720px;margin:0 auto;background:#fff;border-radius:14px;padding:24px 28px;box-shadow:0 2px 10px #0002}}
h1{{font-size:22px;color:#0b6e4f;margin-top:0}} h2{{font-size:17px;color:#0b6e4f;margin-top:26px}}
small{{color:#6b7280}} li{{margin:4px 0}}
</style></head><body><main>
<small>Collège Catholique Bilingue de la Retraite, Yaoundé · Application « Réservation - Collège de la Retraite »</small>
<h1>{title}</h1>{body}
<p><small>Dernière mise à jour : {updated}</small></p>
</main></body></html>"""


def _page(title: str, body: str) -> HTMLResponse:
    return HTMLResponse(PAGE.format(title=html.escape(title), body=body, updated=UPDATED))


@router.get("/privacy", response_class=HTMLResponse)
def privacy_policy():
    contact = html.escape(settings.CONTACT_EMAIL)
    body = f"""
<p>Cette application permet de réserver le gymnase, la salle des fêtes et les autres espaces du Collège Catholique
Bilingue de la Retraite, de payer la location et de recevoir un reçu. Voici, simplement, ce que nous faisons de vos
données.</p>

<h2>Les données que nous recueillons</h2>
<ul>
<li><b>Votre compte</b> : nom complet, adresse email, numéro de téléphone (facultatif) et mot de passe. Le mot de passe
n'est jamais conservé en clair : seule une empreinte chiffrée est enregistrée.</li>
<li><b>Vos réservations</b> : espace, date, horaires, catégorie tarifaire choisie, prestations (chaises, tables,
sonorisation), montant, caution, moyen de paiement et référence de paiement, code de sécurité, reçu PDF.</li>
<li><b>Vos messages à l'assistant intelligent</b>, si vous l'utilisez.</li>
<li><b>Des journaux techniques</b> du serveur (date, action effectuée, erreurs) pour assurer la sécurité et réparer
les pannes.</li>
</ul>
<p>Nous ne demandons ni votre position, ni vos contacts, ni vos photos, ni votre micro, ni votre caméra.</p>

<h2>Pourquoi nous les utilisons</h2>
<ul>
<li>créer et protéger votre compte ;</li>
<li>vérifier qu'un créneau est libre, enregistrer votre réservation et vous envoyer le reçu ;</li>
<li>permettre à l'administration du Collège de valider les réservations et de suivre ses recettes ;</li>
<li>vous envoyer un code par email si vous oubliez votre mot de passe ;</li>
<li>vérifier l'authenticité d'un reçu grâce à son code QR (la page de vérification n'affiche que l'espace, la date, les
horaires, le statut et vos initiales).</li>
</ul>

<h2>Avec qui elles sont partagées</h2>
<ul>
<li>L'<b>administration du Collège</b>, pour gérer les réservations.</li>
<li>Notre <b>hébergeur</b>, qui fait fonctionner le serveur et la base de données.</li>
<li><b>Anthropic</b> (assistant « Claude »), uniquement si vous utilisez l'assistant : les messages que vous lui écrivez lui
sont envoyés pour qu'il puisse répondre. N'y écrivez pas d'informations sensibles.</li>
<li>Les <b>opérateurs de paiement</b> (Orange Money, MTN Mobile Money...) lorsque le paiement réel sera activé.</li>
</ul>
<p>Nous ne vendons pas vos données et nous n'affichons aucune publicité.</p>

<h2>Combien de temps nous les gardons</h2>
<p>Vos données de compte sont conservées tant que votre compte existe. Si vous supprimez votre compte, votre nom, votre
email, votre téléphone et votre mot de passe sont effacés immédiatement. Les réservations et les reçus restent, sans
aucun nom, parce que ce sont des pièces comptables du Collège.</p>

<h2>Vos droits</h2>
<ul>
<li><b>Supprimer votre compte</b> : directement dans l'application (Accueil, « Supprimer mon compte »), ou en suivant les
explications de la page <a href="/account-deletion">suppression de compte</a>.</li>
<li><b>Modifier ou obtenir vos données</b> : écrivez-nous à <a href="mailto:{contact}">{contact}</a>.</li>
</ul>

<h2>Sécurité</h2>
<p>Les échanges entre l'application et le serveur sont chiffrés (HTTPS). Les mots de passe sont chiffrés, les reçus sont
signés pour éviter les faux, et l'accès aux données de l'administration est réservé aux comptes autorisés.</p>

<h2>Enfants</h2>
<p>L'application s'adresse aux adultes (parents, associations, entreprises, institutions) qui louent les espaces du
Collège. Elle n'est pas destinée aux enfants.</p>

<h2>Nous contacter</h2>
<p>Pour toute question sur cette politique : <a href="mailto:{contact}">{contact}</a>.</p>
"""
    return _page("Politique de confidentialité", body)


@router.get("/account-deletion", response_class=HTMLResponse)
def account_deletion():
    contact = html.escape(settings.CONTACT_EMAIL)
    body = f"""
<p>Vous pouvez supprimer votre compte à tout moment, de deux façons.</p>

<h2>1. Depuis l'application</h2>
<ol>
<li>Ouvrez l'application et connectez-vous.</li>
<li>Sur l'écran d'accueil, appuyez sur <b>« Supprimer mon compte »</b>.</li>
<li>Saisissez votre mot de passe et confirmez.</li>
</ol>

<h2>2. Par email</h2>
<p>Écrivez à <a href="mailto:{contact}">{contact}</a> depuis l'adresse email de votre compte, avec pour objet
« Suppression de mon compte ». Nous supprimons le compte dans un délai raisonnable.</p>

<h2>Ce qui est supprimé</h2>
<ul>
<li>votre nom, votre adresse email, votre numéro de téléphone et votre mot de passe : <b>effacés immédiatement</b> ;</li>
<li>vos demandes de réinitialisation de mot de passe : effacées ;</li>
<li>vos réservations en attente de validation à venir : annulées.</li>
</ul>

<h2>Ce qui est conservé</h2>
<p>Les réservations déjà faites et leurs reçus sont conservés <b>sans aucun nom</b>, parce que ce sont des pièces
comptables du Collège.</p>

<h2>Bon à savoir</h2>
<p>Si vous avez une réservation validée à venir, annulez-la ou contactez l'administration avant de supprimer votre compte.</p>
"""
    return _page("Supprimer mon compte et mes données", body)
