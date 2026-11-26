# TransitManager

Application Flask/SQLite de gestion du transport.

## Déploiement sur Render

1. Publiez ce dossier dans un dépôt GitHub.
2. Sur Render, choisissez **New > Blueprint** puis sélectionnez le dépôt.
3. Render utilisera `render.yaml` pour créer le service web et le disque de données.
4. Attendez la fin du déploiement puis ouvrez l’URL HTTPS fournie par Render.

## Exécution locale

```powershell
python -m pip install -r requirements.txt
python app.py
```

L’application sera disponible sur `http://127.0.0.1:5000`.

## Comptes de démonstration

- Administrateur : `admin` / `Admin@2026`
- Finance : `finance` / `Finance@2026`
- Employé : `employe` / `Employe@2026`

Changez ces mots de passe avant une utilisation publique réelle.
