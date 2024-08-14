# Email Scraper

## Description

**Email Scraper** est un outil automatisé conçu pour extraire des adresses e-mail à partir de sites web. Il parcourt les pages web pour identifier des adresses e-mail correspondant à un suffixe spécifique (comme `@gmail.com`) et les enregistre dans des fichiers de log organisés par domaine.

## Fonctionnalités

- **Scraping de pages web :** Extraction d'adresses e-mail à partir de pages HTML.
- **Filtrage des e-mails :** Option pour cibler les adresses e-mail selon un suffixe spécifique (par exemple, `@gmail.com`).
- **Exploration de domaines multiples :** Exploration automatique de liens internes pour couvrir un maximum de pages.
- **Enregistrement des résultats :** Sauvegarde des e-mails extraits dans des fichiers de log structurés.
- **Interface en ligne de commande :** Simple à utiliser, accessible à tous.

## Installation

1. Téléchargez le fichier `.zip` du projet.
2. Exécutez le fichier `start.bat` pour lancer le programme.

## Utilisation

1. Lancez le script `emailscrapper.py`.

2. Entrez l'URL du domaine à scraper (par exemple `https://www.example.com`).

3. Spécifiez le suffixe des e-mails à extraire, comme `@gmail.com`, ou sélectionnez `all` pour capturer toutes les adresses.

4. Le programme explorera automatiquement les pages du domaine, extraira les e-mails trouvés, et les enregistrera dans le dossier `logs`.

5. Les fichiers de log sont classés par domaine et contiennent les adresses e-mail extraites.

## Configuration

Vous pouvez personnaliser certains paramètres directement dans le fichier `emailscrapper.py`, tels que l'agent utilisateur pour les requêtes HTTP, ou les domaines à ignorer.

## Avertissement

Cet outil doit être utilisé de manière éthique et légale. Veillez à obtenir les autorisations nécessaires avant de scraper un site web, surtout si vous envisagez d'utiliser les informations collectées à des fins commerciales.

## Auteur

Créé par **l4tence**.

---

**Note :** Ce projet est fourni "tel quel", sans garantie d'aucune sorte. Utilisez-le à vos propres risques.
