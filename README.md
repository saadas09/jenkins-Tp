# Campus Café

Petit atelier CI/CD distribué : Flask, 9 tests, Jenkins sur agents Windows et Docker Linux. Un café coûte **12 DH**, une commande contient **1 à 10 cafés**.

## En local (PowerShell, Python 3.12)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -v
.\.venv\Scripts\waitress-serve.exe --listen=0.0.0.0:5000 app:app
```

Ouvrir http://localhost:5000 ; `/commande/2` renvoie `{"devise":"DH","quantite":2,"total":24}`. Dans un autre terminal : `.\.venv\Scripts\python.exe smoke.py`. `/health` expose `status`, `build` et `machine`. Sans `BUILD_NUMBER`, la livraison vaut `local`.

## Docker Desktop (conteneurs Linux)

```powershell
$env:BUILD_NUMBER = "demo"
docker compose -p campus-cafe up -d --build
py -3.12 smoke.py
docker compose -p campus-cafe down
```

Le port 5000 doit être libre. Un seul déploiement `campus-cafe` est prévu par PC ; les différents étudiants déploient sur des PC distincts.

## Jenkins

Sur le contrôleur commun : plugins Git, Pipeline et JUnit ; aucun executor sur le nœud intégré. Pour chaque étudiant, créer un agent Windows `agent-cafe-NN`, label `cafe-NN`, un executor, connecté au contrôleur. Git, Java compatible, `py -3.12` et Docker Desktop doivent être accessibles au compte de l’agent.

Créer le job Pipeline `campus-cafe-NN`. Cocher **This project is parameterized**, ajouter le **String Parameter** `AGENT_LABEL`, valeur propre à l’étudiant, par exemple `cafe-07`. Le Jenkinsfile ne redéfinit pas ce paramètre.

Choisir **Pipeline script from SCM → Git**, URL publique de ce dépôt, credentials **none**, branche `*/main`, Script Path `Jenkinsfile`. Lancer **Build with Parameters**, vérifier le label. Le pipeline affiche le PC, le nœud, le workspace et le commit, lance 5 tests de prix et 4 tests API en parallèle, puis déploie seulement si les tests réussissent. Les rapports `prix.xml`, `api.xml` et `coverage.xml` sont publiés/archivés même en cas d’échec, s’ils existent.

`hostname` dans la console Jenkins désigne le PC Windows. `machine` dans `/health` utilise `socket.gethostname()` : sous Docker, c’est le nom du conteneur. Jenkins transmet son `BUILD_NUMBER` à Compose.

## Exercices facultatifs

Aucun déclencheur automatique n’est activé. Dans votre fork, ajouter avant `stages` l’un des blocs suivants, puis lancer un build manuel pour appliquer la configuration :

```groovy
triggers { pollSCM('H/5 * * * *') } // vérifie les changements
// Ou : triggers { cron('H/5 * * * *') } // même sans changement
```

Supprimer ensuite le bloc et relancer un build manuel. Pour ignorer les tests si seul `README.md` change, ajouter avant `parallel` dans `Tests paralleles` :

```groovy
when {
    expression {
        def files = []
        for (cs in currentBuild.changeSets) {
            for (item in cs.items) { files.addAll(item.affectedPaths) }
        }
        return files.isEmpty() || files.any { it != 'README.md' }
    }
}
```

Cette condition reste un exercice : elle laisse aussi passer la livraison quand les tests sont ignorés.

**Bloquer une livraison :** dans `calculer_total` (`app.py`), remplacer `return quantite * PRIX_CAFE` par `return quantite + PRIX_CAFE`. Committer dans votre fork : 4 tests doivent échouer et Jenkins doit ignorer la livraison. Rétablir la multiplication, committer et vérifier le retour au vert.

Les vérifications réalisées et leurs limites figurent dans [VALIDATION.md](VALIDATION.md).
test de declenchement auto jenkins
sbnato
