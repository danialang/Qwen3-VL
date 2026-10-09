"""Génère les diagrammes UML du projet (style PowerAMC) à partir de la structure réelle de l'application.

Utilisation :  python generer_diagrammes.py        -> crée les fichiers .png dans ce dossier.
"""
import os

from dessin import (BLACK, LINE, WHITE, Canvas, associate, associate_side, class_box, action, comm_messages, comm_object, component, decision, elbow, final_node, initial_node, link_uc, node3d, sequence, state, usecase)

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


# ============================================================ 10. DIAGRAMME D'ACTIVITÉ (couloirs)
def activite():
    Y = 0.86                       # compression verticale
    cv = Canvas(1440, 1490)
    X1, X2, X3 = 440, 1000, 1440   # fin des couloirs : Client | Système | Administrateur
    top = 56
    for x0, x1, name in [(0, X1, "Client"), (X1, X2, "Système"), (X2, X3, "Administrateur")]:
        cv.rect(x0, 8, x1 - x0, 40, shadow=False)
        cv.text((x0 + x1) / 2, 28, name, size=13, bold=True, anchor="mm")
        cv.d.rectangle([cv.p(x0), cv.p(top - 8), cv.p(x1), cv.p(1480)], outline=LINE, width=cv.p(1))
    def y(v): return v * Y
    C, M, SD, A = 240, 600, 860, 1220          # axes : client, système (flux), système (branches), administrateur

    ini = initial_node(cv, C, y(110))
    a1 = action(cv, C, y(190), "S'authentifier")
    a2 = action(cv, M, y(290), "Vérifier les identifiants")
    d1 = decision(cv, M, y(400), "Identifiants\nvalides ?")
    a3 = action(cv, SD, y(400), "Afficher l'erreur\nde connexion", w=200)
    f1 = final_node(cv, SD, y(500))
    a4 = action(cv, C, y(520), "Choisir la salle, la date\net l'horaire")
    a5 = action(cv, C, y(610), "Accepter le règlement\nintérieur")
    a6 = action(cv, M, y(700), "Vérifier la disponibilité\ndu créneau")
    d2 = decision(cv, M, y(805), "Créneau\nlibre ?")
    a7 = action(cv, SD, y(805), "Refuser et proposer la\nprochaine date disponible", w=210)
    a8 = action(cv, M, y(920), "Enregistrer la réservation (en attente)\net générer le code de sécurité", w=250)
    a9 = action(cv, C, y(1020), "Payer la réservation\n(moyen de paiement + référence)", w=250)
    a10 = action(cv, M, y(1120), "Enregistrer le paiement")
    a11 = action(cv, A, y(1210), "Examiner la demande\nde réservation")
    d3 = decision(cv, A, y(1320), "Réservation\nvalidée ?")
    a12 = action(cv, SD, y(1320), "Annuler la réservation", w=200)
    f2 = final_node(cv, SD, y(1385))
    a13 = action(cv, M, y(1500), "Passer la réservation\nà l'état « Validée »")
    a14 = action(cv, M, y(1590), "Générer le reçu PDF\n(code de sécurité + QR code)", w=240)
    a15 = action(cv, C, y(1680), "Télécharger le reçu", w=200)
    f3 = final_node(cv, M, y(1680))

    elbow(cv, [(C, ini["b"]), (C, a1["t"])])
    elbow(cv, [(a1["r"], a1["cy"]), (M, a1["cy"]), (M, a2["t"])])
    elbow(cv, [(M, a2["b"]), (M, d1["t"])])
    elbow(cv, [(d1["r"], d1["cy"]), (a3["l"], a3["cy"])], "[non]", 732, d1["cy"] - 26)
    elbow(cv, [(SD, a3["b"]), (SD, f1["t"])])
    elbow(cv, [(M, d1["b"]), (M, y(460)), (C, y(460)), (C, a4["t"])], "[oui]", 520, y(460) - 18)
    elbow(cv, [(C, a4["b"]), (C, a5["t"])])
    elbow(cv, [(a5["r"], a5["cy"]), (M, a5["cy"]), (M, a6["t"])])
    elbow(cv, [(M, a6["b"]), (M, d2["t"])])
    elbow(cv, [(d2["r"], d2["cy"]), (a7["l"], a7["cy"])], "[occupé]", 732, d2["cy"] - 26)
    elbow(cv, [(SD, a7["t"]), (SD, y(560)), (a4["r"] + 10, y(560)), (a4["r"] + 10, a4["cy"]), (a4["r"], a4["cy"])])
    elbow(cv, [(M, d2["b"]), (M, a8["t"])], "[libre]", 650, d2["b"] + 8)
    elbow(cv, [(a8["l"], a8["cy"]), (C, a8["cy"]), (C, a9["t"])])
    elbow(cv, [(C, a9["b"]), (C, a10["cy"]), (a10["l"], a10["cy"])])
    elbow(cv, [(a10["r"], a10["cy"]), (A, a10["cy"]), (A, a11["t"])])
    elbow(cv, [(A, a11["b"]), (A, d3["t"])])
    elbow(cv, [(d3["l"], d3["cy"]), (a12["r"], a12["cy"])], "[non]", 1060, d3["cy"] - 20)
    elbow(cv, [(SD, a12["b"]), (SD, f2["t"])])
    elbow(cv, [(A, d3["b"]), (A, y(1445)), (M + 150, y(1445)), (M + 150, a13["cy"] - 5), (a13["r"], a13["cy"] - 5)], "[oui]", 1280, d3["b"] + 4)
    elbow(cv, [(M, a13["b"]), (M, a14["t"])])
    elbow(cv, [(a14["l"], a14["cy"]), (C, a14["cy"]), (C, a15["t"])])
    elbow(cv, [(a15["r"], a15["cy"]), (f3["l"], f3["cy"])])
    cv.save(out("10_diagramme_activite_reservation.png"))


# ============================================================ 11. DIAGRAMME DE COMMUNICATION
def communication():
    cv = Canvas(1800, 560)
    cl = comm_object(cv, 110, 230, "Client", actor=True)
    app = comm_object(cv, 640, 230, ":Application mobile")
    api = comm_object(cv, 1170, 230, ":API FastAPI")
    db = comm_object(cv, 1690, 230, ":Base MySQL")
    adm = comm_object(cv, 640, 470, "Administrateur", actor=True)
    cv.line([(cl["r"] + 6, 230), (app["l"], 230)])
    cv.line([(app["r"], 230), (api["l"], 230)])
    cv.line([(api["r"], 230), (db["l"], 230)])
    cv.line([(640, app["b"]), (640, adm["t"] - 8)])
    comm_messages(cv, cl["r"], app["l"], 230, [
        ("1 : s'authentifier()", ">"),
        ("2 : choisir la salle, la date et l'horaire", ">"),
        ("3 : accepter le règlement intérieur", ">"),
        ("5 : payer la réservation", ">"),
    ])
    comm_messages(cv, app["r"], api["l"], 230, [
        ("1.1 : POST /auth/login", ">"),
        ("1.3 : authentifié (jeton JWT)", "<"),
        ("4 : POST /reservations", ">"),
        ("5.1 : POST /reservations/{id}/pay", ">"),
        ("6.1 : POST /reservations/{id}/validate", ">"),
    ])
    comm_messages(cv, api["r"], db["l"], 230, [
        ("1.2 : vérifier l'email et le mot de passe", ">"),
        ("4.1 : vérifier la disponibilité du créneau", ">"),
        ("4.2 : enregistrer la réservation et le code", ">"),
        ("5.2 : enregistrer le paiement", ">"),
        ("6.2 : valider et enregistrer le reçu", ">"),
    ])
    cv.line([(660, 340), (660, 392)])
    cv.head((660, 392), (660, 340), "filled", size=8)
    cv.text(676, 366, "6 : valider la réservation", size=11, anchor="lm")
    cv.save(out("11_diagramme_communication_reservation.png"))


# ============================================================ 12. COMMUNICATION (style du rapport : cyan / bleu)
def communication_rapport(path):
    import dessin
    saved = (dessin.YELLOW, dessin.LINE, dessin.SHADOW, dessin.FONT, dessin.BOLD)
    dessin.YELLOW, dessin.LINE, dessin.SHADOW = (192, 255, 255), (30, 144, 255), (170, 170, 170)
    dessin.FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
    dessin.BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
    try:
        F, M = 16, 15                      # tailles : objets, messages
        cv = Canvas(1800, 760)
        cv.text(900, 22, "Diagramme de communication", size=22, bold=True, anchor="ma")
        cv.text(900, 58, "Réservation d'une installation", size=16, bold=True, anchor="ma")
        cl = comm_object(cv, 90, 250, ":Client", actor=True, fs=F)
        app = comm_object(cv, 560, 250, ":ApplicationFlutter", w=240, h=52, fs=F)
        api = comm_object(cv, 1060, 250, ":ApiFastAPI", w=210, h=52, fs=F)
        lg = comm_object(cv, 1060, 590, ":LogiqueReservation", w=250, h=52, fs=F)
        db = comm_object(cv, 1680, 590, ":BaseMySQL", w=210, h=52, fs=F)
        cv.line([(cl["r"] + 6, 250), (app["l"], 250)])
        cv.line([(app["r"], 250), (api["l"], 250)])
        cv.line([(1060, api["b"]), (1060, lg["t"])])
        cv.line([(lg["r"], 590), (db["l"], 590)])
        comm_messages(cv, cl["r"], app["l"], 250, [
            ("1 : s'authentifier()", ">"),
            ("3 : demanderRéservation()", ">"),
        ], fs=M)
        comm_messages(cv, cl["r"], app["l"], 250, [
            ("2 : authentifié (jeton JWT)", "<"),
            ("12 : afficherConfirmation()", "<"),
        ], above=False, fs=M)
        comm_messages(cv, app["r"], api["l"], 250, [("4 : créerRéservation()", ">")], fs=M)
        comm_messages(cv, app["r"], api["l"], 250, [("11 : retournerCodeEtStatut()", "<")], above=False, fs=M)
        # liaison verticale API <-> Logique : 5 vers le bas, 10 vers le haut
        cv.line([(1090, 350), (1090, 440)])
        cv.head((1090, 440), (1090, 350), "filled", size=10)
        cv.text(1106, 395, "5 : créerRéservation()", size=M, anchor="lm")
        cv.line([(1030, 440), (1030, 350)])
        cv.head((1030, 350), (1030, 440), "filled", size=10)
        cv.text(1014, 395, "10 : retournerRéservation()", size=M, anchor="rm")
        comm_messages(cv, lg["r"], db["l"], 590, [
            ("6 : vérifierChevauchement()", ">"),
            ("8 : enregistrerRéservation()", ">"),
            ("9 : enregistrerCodeSécurité()", ">"),
        ], fs=M)
        comm_messages(cv, lg["r"], db["l"], 590, [("7 : retournerCréneauxOccupés()", "<")], above=False, fs=M)
        cv.save(path)
    finally:
        dessin.YELLOW, dessin.LINE, dessin.SHADOW, dessin.FONT, dessin.BOLD = saved


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
    activite()
    communication()
    communication_rapport(out("fig07_communication_reservation.png"))
    print("Diagrammes générés dans", ICI)
