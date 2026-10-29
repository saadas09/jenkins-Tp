"""Application pédagogique Campus Café."""
import os
import socket

from flask import Flask, jsonify, render_template

app = Flask(__name__)
PRIX_CAFE = 12


def calculer_total(quantite):
    if not isinstance(quantite, int) or isinstance(quantite, bool) or not 1 <= quantite <= 10:
        raise ValueError("La quantité doit être comprise entre 1 et 10.")
    return quantite * PRIX_CAFE


@app.get("/")
def accueil():
    return render_template("index.html", prix=PRIX_CAFE, build=os.getenv("BUILD_NUMBER", "local"))


@app.get("/commande/<int:quantite>")
def commande(quantite):
    try:
        total = calculer_total(quantite)
    except ValueError as erreur:
        return jsonify(erreur=str(erreur)), 400
    return jsonify(quantite=quantite, total=total, devise="DH")


# Le convertisseur int standard de Flask ne reconnaît pas les entiers négatifs.
@app.get("/commande/<int(signed=True):quantite>")
def commande_signee(quantite):
    return commande(quantite)


@app.get("/health")
def health():
    return jsonify(status="ok", build=os.getenv("BUILD_NUMBER", "local"), machine=socket.gethostname())
