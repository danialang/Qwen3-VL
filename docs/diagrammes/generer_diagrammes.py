"""Génère les diagrammes UML du projet (style PowerAMC) à partir de la structure réelle de l'application.

Utilisation :  python generer_diagrammes.py        -> crée les fichiers .png dans ce dossier.
"""
import os

from dessin import (BLACK, LINE, WHITE, Canvas, associate, associate_side, class_box, component, elbow, link_uc, node3d, sequence, state, usecase)

ICI = os.path.dirname(os.path.abspath(__file__))


def out(name):
    return os.path.join(ICI, name)


# ============================================================ 1. CAS D'UTILISATION : CLIENT
def cas_client():
    cv = Canvas(1250, 1230)
    ys = {}
    L, R = 520, 960
    u = {}
    u["inscrire"] = usecase(cv, L, 70, "S'inscrire", 330)
    u["connecter"] = usecase(cv, L, 160, "Se connecter", 330)
    u["changer"] = usecase(cv, L, 250, "Changer son mot de passe", 330)
    u["reinit"] = usecase(cv, L, 350, "Réinitialiser son\nmot de passe", 330)
    u["code"] = usecase(cv, R, 350, "Envoyer un code\npar email")
    u["dispo"] = usecase(cv, L, 460, "Consulter les disponibilités\ndes salles", 330)
    u["rules"] = usecase(cv, R, 570, "Accepter le règlement\nintérieur")
    u["reserver"] = usecase(cv, L, 650, "Réserver une salle", 330)
    u["suggest"] = usecase(cv, R, 740, "Proposer la prochaine\ndate disponible")
    u["payer"] = usecase(cv, L, 860, "Payer la réservation", 330)
    u["mes"] = usecase(cv, L, 960, "Consulter mes réservations", 330)
    u["recu"] = usecase(cv, L, 1050, "Télécharger le reçu PDF", 330)
    u["assistant"] = usecase(cv, L, 1150, "Discuter avec l'assistant IA\nde réservation", 330)

    client = cv.actor(90, 560, "Client")
    for k in ["inscrire", "connecter", "changer", "reinit", "dispo", "reserver", "payer", "mes", "recu", "assistant"]:
        associate_side(cv, client, u[k], "left")

    cv.label_over(90, 560 + 9 + 56, "Client")
    email = cv.actor(1130, 300, "Service\nd'email")
    associate(cv, email, u["code"])
    paiement = cv.actor(1130, 820, "Service\nde paiement")
    associate_side(cv, paiement, u["payer"], "right")
    ia = cv.actor(1130, 1100, "Assistant IA\n(Claude)")
    associate_side(cv, ia, u["assistant"], "right")

    link_uc(cv, u["reinit"], u["code"], "«include»")
    link_uc(cv, u["reserver"], u["rules"], "«include»")
    link_uc(cv, u["suggest"], u["reserver"], "«extend»")
    cv.save(out("01_cas_utilisation_client.png"))


# ============================================================ 2. CAS D'UTILISATION : ADMINISTRATION
def cas_admin():
    cv = Canvas(1250, 1130)
    L, R = 520, 970
    u = {}
    u["connecter"] = usecase(cv, L, 70, "Se connecter", 330)
    u["changer"] = usecase(cv, L, 160, "Changer son mot de passe", 330)
    u["dash"] = usecase(cv, L, 270, "Consulter le tableau de bord\n(statistiques)", 330)
    u["revenus"] = usecase(cv, R, 270, "Afficher les revenus\n(mois, à venir, année)")
    u["comptes"] = usecase(cv, L, 380, "Consulter les comptes inscrits", 330)
    u["toutes"] = usecase(cv, L, 470, "Consulter toutes les réservations", 330)
    u["valider"] = usecase(cv, L, 580, "Valider une réservation", 330)
    u["recu"] = usecase(cv, R, 580, "Générer le reçu PDF\n(code de sécurité + QR code)")
    u["interne"] = usecase(cv, L, 700, "Réserver pour le Collège\n(réservation interne gratuite)", 330)
    u["conflit"] = usecase(cv, R, 700, "Vérifier les conflits\n(priorité du Collège)")
    u["assistant"] = usecase(cv, L, 830, "Interroger l'assistant IA admin", 330)
    u["verifier"] = usecase(cv, 880, 990, "Vérifier l'authenticité\nd'un reçu (scan du QR)")

    admin = cv.actor(90, 330, "Administrateur")
    dev = cv.actor(90, 700, "Développeur")
    cv.line([(90, 689), (90, 436)])               # généralisation Développeur -> Administrateur
    cv.head((90, 436), (90, 689), "hollow", size=14)
    for k in ["connecter", "changer", "dash", "comptes", "toutes", "valider", "interne", "assistant"]:
        associate_side(cv, admin, u[k], "left")

    cv.label_over(90, 330 + 9 + 56, "Administrateur")
    ia = cv.actor(1130, 830, "Assistant IA\n(Claude)")
    associate_side(cv, ia, u["assistant"], "right")
    controleur = cv.actor(1130, 960, "Contrôleur\n(tout visiteur\nqui scanne)")
    associate_side(cv, controleur, u["verifier"], "right")

    link_uc(cv, u["dash"], u["revenus"], "«include»")
    link_uc(cv, u["valider"], u["recu"], "«include»")
    link_uc(cv, u["interne"], u["conflit"], "«include»")
    cv.save(out("02_cas_utilisation_administration.png"))


# ============================================================ 3. DIAGRAMME DE CLASSES
def classes():
    cv = Canvas(1640, 760)
    user = class_box(cv, 70, 60, 410, "User", [
        "- id : Integer",
        "- email : String(191)  {unique}",
        "- password_hash : String(255)",
        "- full_name : String(255)",
        "- phone : String(30)",
        "- role : UserRole",
        "- created_at : DateTime",
    ], [
        "+ sInscrire()",
        "+ seConnecter() : jeton JWT",
        "+ changerMotDePasse()",
        "+ reinitialiserMotDePasse(code)",
    ])
    reservation = class_box(cv, 740, 60, 400, "Reservation", [
        "- id : Integer",
        "- user_id : Integer  {FK}",
        "- room : RoomType",
        "- event_date : Date",
        "- start_time : Time",
        "- end_time : Time",
        "- status : ReservationStatus",
        "- amount : Numeric(12,2)",
        "- is_internal : Boolean",
        "- accepted_rules : Boolean",
        "- payment_method : String(50)",
        "- payment_reference : String(255)",
        "- paid_at : DateTime",
        "- created_at : DateTime",
    ], [
        "+ creer()   + payer()",
        "+ valider()   + annuler()",
    ])
    code = class_box(cv, 1330, 60, 270, "SecurityCode", [
        "- id : Integer",
        "- reservation_id : Integer  {FK}",
        "- code : String(64)  {unique}",
        "- created_at : DateTime",
    ], ["+ generer()"])
    recu = class_box(cv, 1330, 300, 270, "Receipt", [
        "- id : Integer",
        "- reservation_id : Integer  {FK}",
        "- pdf_path : String(500)",
        "- created_at : DateTime",
    ], ["+ genererPDF()", "+ verifierQR()"])
    reset = class_box(cv, 70, 440, 330, "PasswordReset", [
        "- id : Integer",
        "- user_id : Integer  {FK}",
        "- code_hash : String(64)",
        "- expires_at : DateTime",
        "- attempts : Integer",
        "- used : Boolean",
        "- created_at : DateTime",
    ], ["+ verifierCode()"])
    role = class_box(cv, 430, 470, 190, "UserRole", ["client", "admin", "dev"], stereotype="enumeration")
    room = class_box(cv, 740, 540, 190, "RoomType", ["gymnase", "salle_fetes"], stereotype="enumeration")
    status = class_box(cv, 960, 540, 190, "ReservationStatus", ["pending", "validated", "cancelled"], stereotype="enumeration")

    def mult(x, y, txt, anchor="la"):
        cv.text(x, y, txt, size=11, anchor=anchor)

    # User 1 --- 0..* Reservation
    cv.line([(480, 150), (740, 150)])
    cv.text(610, 138, "effectue", size=11, anchor="md")
    mult(488, 154, "1")
    mult(732, 154, "0..*", "ra")
    # Reservation <>--- SecurityCode (composition)
    cv.line([(1140, 120), (1330, 120)])
    cv.head((1140, 120), (1330, 120), "diamond", size=9)
    cv.text(1235, 108, "possède", size=11, anchor="md")
    mult(1166, 124, "1")
    mult(1322, 124, "1", "ra")
    # Reservation <>--- Receipt (composition)
    cv.line([(1140, 250), (1235, 250), (1235, 340), (1330, 340)])
    cv.head((1140, 250), (1235, 250), "diamond", size=9)
    cv.text(1262, 300, "génère", size=11, anchor="lm")
    mult(1166, 254, "1")
    mult(1322, 344, "0..1", "ra")
    # User 1 --- 0..* PasswordReset
    cv.line([(200, 60 + user["h"]), (200, 440)])
    cv.text(212, 410, "demande", size=11, anchor="lm")
    mult(208, 60 + user["h"] + 4, "1")
    mult(208, 418, "0..*")
    # dépendances vers les énumérations
    for src, dst, lab, sx in [(user, role, "role", 460), (reservation, room, "room", 800), (reservation, status, "status", 1050)]:
        cv.line([(sx, src["y"] + src["h"]), (sx, dst["y"])], dash=True)
        cv.head((sx, dst["y"]), (sx, src["y"] + src["h"]), "open")
        cv.text(sx + 8, dst["y"] - 26, lab, size=11)
    cv.save(out("03_diagramme_de_classes.png"))


# ============================================================ 4. SÉQUENCE : RÉSERVER ET PAYER
def seq_reserver():
    sequence(out("04_sequence_reserver_et_payer.png"),
             [("Client", "actor"), ("Application mobile\n(Flutter)", "object"), ("API FastAPI", "object"), ("Base MySQL", "object")],
             [
                 ("msg", "Client", "Application mobile\n(Flutter)", "choisir salle, date et horaire", "call"),
                 ("msg", "Client", "Application mobile\n(Flutter)", "accepter le règlement intérieur", "call"),
                 ("msg", "Application mobile\n(Flutter)", "API FastAPI", "POST /reservations  (jeton JWT)", "call", True),
                 ("msg", "API FastAPI", "Base MySQL", "SELECT créneaux qui se chevauchent", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "résultat", "return"),
                 ("alt", "créneau libre"),
                 ("msg", "API FastAPI", "Base MySQL", "INSERT reservation (pending, montant)", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "id de la réservation", "return"),
                 ("msg", "API FastAPI", "Base MySQL", "INSERT security_code", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "ok", "return"),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "201 Réservation créée", "return"),
                 ("msg", "Application mobile\n(Flutter)", "Client", "afficher l'écran de paiement", "return"),
                 ("msg", "Client", "Application mobile\n(Flutter)", "choisir le moyen de paiement + référence", "call"),
                 ("msg", "Application mobile\n(Flutter)", "API FastAPI", "POST /reservations/{id}/pay", "call", True),
                 ("msg", "API FastAPI", "Base MySQL", "UPDATE paiement (méthode, référence, date)", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "ok", "return"),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "réservation payée, en attente de validation", "return"),
                 ("else", "créneau occupé (priorité du Collège)"),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "409 Conflit + prochaine date disponible", "return"),
                 ("msg", "Application mobile\n(Flutter)", "Client", "proposer la nouvelle date", "return"),
                 ("end",),
             ])


# ============================================================ 5. SÉQUENCE : VALIDER ET GÉNÉRER LE REÇU
def seq_valider():
    sequence(out("05_sequence_valider_et_recu.png"),
             [("Administrateur", "actor"), ("Application mobile\n(Flutter)", "object"), ("API FastAPI", "object"), ("Base MySQL", "object")],
             [
                 ("msg", "Administrateur", "Application mobile\n(Flutter)", "ouvrir « Réservations & validations »", "call"),
                 ("msg", "Application mobile\n(Flutter)", "API FastAPI", "GET /reservations", "call", True),
                 ("msg", "API FastAPI", "Base MySQL", "SELECT toutes les réservations", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "liste", "return"),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "liste des réservations", "return"),
                 ("msg", "Administrateur", "Application mobile\n(Flutter)", "valider la réservation", "call"),
                 ("msg", "Application mobile\n(Flutter)", "API FastAPI", "POST /reservations/{id}/validate", "call", True),
                 ("self", "API FastAPI", "vérifier le rôle (admin ou dev)", True),
                 ("msg", "API FastAPI", "Base MySQL", "UPDATE statut = validated", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "ok", "return"),
                 ("self", "API FastAPI", "générer le reçu PDF\n(code de sécurité + QR signé)", True),
                 ("msg", "API FastAPI", "Base MySQL", "INSERT receipt", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "ok", "return"),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "réservation validée", "return"),
                 ("msg", "Application mobile\n(Flutter)", "Administrateur", "afficher le nouveau statut", "return"),
             ])


# ============================================================ 6. SÉQUENCE : VÉRIFIER UN REÇU (QR)
def seq_verifier():
    sequence(out("06_sequence_verifier_recu_qr.png"),
             [("Contrôleur", "actor"), ("Téléphone\n(appareil photo)", "object"), ("API FastAPI", "object"), ("Base MySQL", "object")],
             [
                 ("msg", "Contrôleur", "Téléphone\n(appareil photo)", "scanner le QR code du reçu", "call"),
                 ("msg", "Téléphone\n(appareil photo)", "API FastAPI", "GET /verify/{id}/{jeton}", "call", True),
                 ("msg", "API FastAPI", "Base MySQL", "SELECT réservation + code de sécurité", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "données de la réservation", "return"),
                 ("self", "API FastAPI", "recalculer la signature HMAC\net la comparer au jeton", True),
                 ("alt", "signature correcte"),
                 ("msg", "API FastAPI", "Téléphone\n(appareil photo)", "page « REÇU AUTHENTIQUE » (nom masqué)", "return"),
                 ("else", "signature fausse ou reçu inconnu"),
                 ("msg", "API FastAPI", "Téléphone\n(appareil photo)", "page « REÇU NON AUTHENTIQUE » (404)", "return"),
                 ("end",),
                 ("msg", "Téléphone\n(appareil photo)", "Contrôleur", "afficher le résultat", "return"),
             ])


# ============================================================ 7. SÉQUENCE : MOT DE PASSE OUBLIÉ
def seq_mdp():
    sequence(out("07_sequence_mot_de_passe_oublie.png"),
             [("Client", "actor"), ("Application mobile\n(Flutter)", "object"), ("API FastAPI", "object"),
              ("Base MySQL", "object"), ("Service d'email\n(SMTP)", "object")],
             [
                 ("msg", "Client", "Application mobile\n(Flutter)", "« Mot de passe oublié ? » + email", "call"),
                 ("msg", "Application mobile\n(Flutter)", "API FastAPI", "POST /auth/forgot-password", "call", True),
                 ("msg", "API FastAPI", "Base MySQL", "SELECT utilisateur (sans tenir\ncompte des majuscules)", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "utilisateur", "return"),
                 ("alt", "compte existant, dernier code > 60 s"),
                 ("msg", "API FastAPI", "Base MySQL", "INSERT password_reset (code haché, +15 min)", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "ok", "return"),
                 ("msg", "API FastAPI", "Service d'email\n(SMTP)", "envoyer le code à 6 chiffres", "call", True),
                 ("msg", "Service d'email\n(SMTP)", "API FastAPI", "ok", "return"),
                 ("end",),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "200 même réponse dans tous les cas", "return"),
                 ("msg", "Client", "Application mobile\n(Flutter)", "saisir le code + nouveau mot de passe", "call"),
                 ("msg", "Application mobile\n(Flutter)", "API FastAPI", "POST /auth/reset-password", "call", True),
                 ("msg", "API FastAPI", "Base MySQL", "SELECT dernier code non utilisé", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "code haché, expiration, essais", "return"),
                 ("alt", "code juste, non expiré, moins de 5 essais"),
                 ("msg", "API FastAPI", "Base MySQL", "UPDATE mot de passe haché, code utilisé", "call", True),
                 ("msg", "Base MySQL", "API FastAPI", "ok", "return"),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "200 Mot de passe modifié", "return"),
                 ("else", "code faux, expiré ou bloqué"),
                 ("msg", "API FastAPI", "Application mobile\n(Flutter)", "400 Code invalide ou expiré (essai +1)", "return"),
                 ("end",),
             ], gap=290)


# ============================================================ 8. DÉPLOIEMENT
def deploiement():
    cv = Canvas(1760, 900)
    node3d(cv, 50, 330, 340, 210, "Tablette / téléphone Android", "device")
    app = component(cv, 90, 410, 250, 80, "Application mobile\nFlutter (Dart)\napp-release.apk")
    node3d(cv, 560, 100, 700, 700, "Serveur d'hébergement", "execution environment : Docker")
    caddy = component(cv, 640, 200, 300, 80, "caddy\nHTTPS automatique (optionnel)")
    api = component(cv, 640, 390, 300, 100, "api\nFastAPI + Uvicorn (Python 3.12)\nlogique métier, reçus PDF, QR")
    db = component(cv, 640, 620, 300, 90, "db\nMySQL 8")
    cv.text(965, 640, "volumes Docker :\nbase, reçus PDF, journaux", size=11, anchor="la")
    node3d(cv, 1420, 90, 300, 150, "API Claude (Anthropic)", "cloud")
    node3d(cv, 1420, 310, 300, 150, "Serveur SMTP (Gmail)", "cloud")
    node3d(cv, 1420, 530, 300, 150, "Service de paiement (prévu)", "cloud")
    node3d(cv, 50, 650, 340, 170, "GitHub / GitHub Actions", "cloud")
    component(cv, 90, 730, 250, 60, "build de l'APK Flutter")

    elbow(cv, [(340, 450), (480, 450), (480, 240), (640, 240)], "HTTPS (REST / JSON,\njeton JWT)", 410, 412)
    elbow(cv, [(790, 280), (790, 390)], "HTTP interne", 855, 335)
    elbow(cv, [(790, 490), (790, 620)], "SQL (pymysql, port 3306)", 880, 555)
    elbow(cv, [(940, 420), (1100, 420), (1100, 175), (1420, 175)], "HTTPS (API Claude)", 1340, 150)
    elbow(cv, [(940, 440), (1160, 440), (1160, 385), (1420, 385)], "SMTP (STARTTLS, 587)", 1290, 410)
    elbow(cv, [(940, 470), (1160, 470), (1160, 605), (1420, 605)], "HTTPS (webhook, prévu)", 1290, 580, dash=True)
    elbow(cv, [(215, 664), (215, 540)], "installation de l'APK", 215, 590, dash=True)
    cv.save(out("08_diagramme_de_deploiement.png"))


# ============================================================ 9. ÉTATS D'UNE RÉSERVATION
def etats():
    cv = Canvas(1300, 640)
    pending = state(cv, 340, 250, 260, 90, "En attente\n(pending)")
    validated = state(cv, 960, 250, 260, 90, "Validée\n(validated)")
    cancelled = state(cv, 650, 470, 260, 90, "Annulée\n(cancelled)")
    # états initiaux
    cv.d.ellipse([cv.p(60 - 9), cv.p(250 - 9), cv.p(60 + 9), cv.p(250 + 9)], fill=BLACK)
    elbow(cv, [(69, 250), (210, 250)], "créer()\npar un client", 140, 205)
    cv.d.ellipse([cv.p(960 - 9), cv.p(70 - 9), cv.p(960 + 9), cv.p(70 + 9)], fill=BLACK)
    elbow(cv, [(960, 79), (960, 205)], "créer() par un admin ou dev\n(réservation interne, gratuite)", 1090, 120)
    # paiement : boucle sur « En attente »
    cv.line([(290, 205), (290, 135), (390, 135), (390, 205)])
    cv.head((390, 205), (390, 135), "open")
    cv.text(340, 108, "payer()  [méthode + référence]", size=11, anchor="ma")
    elbow(cv, [(470, 250), (830, 250)], "valider()  [admin ou dev]", 650, 225)
    elbow(cv, [(400, 290), (560, 430)], "annuler()", 440, 380)
    elbow(cv, [(900, 290), (740, 430)], "annuler()", 880, 380)
    # état final
    cv.line([(650, 515), (650, 570)])
    cv.head((650, 570), (650, 515), "open")
    cv.d.ellipse([cv.p(650 - 14), cv.p(584 - 14), cv.p(650 + 14), cv.p(584 + 14)], outline=LINE, width=cv.p(2), fill=WHITE)
    cv.d.ellipse([cv.p(650 - 8), cv.p(584 - 8), cv.p(650 + 8), cv.p(584 + 8)], fill=BLACK)
    cv.save(out("09_diagramme_etats_reservation.png"))


if __name__ == "__main__":
    cas_client()
    cas_admin()
    classes()
    seq_reserver()
    seq_valider()
    seq_verifier()
    seq_mdp()
    deploiement()
    etats()
    print("Diagrammes générés dans", ICI)
