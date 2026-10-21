# Vérification de la version 1.4.0

Testé sur Amazon Fire TV Stick AFTSS, Fire OS 7 / Android API 28 / armeabi-v7a.

- Build Android release réussi ; 9 tests unitaires Android réussis.
- Android Lint : 0 erreur, 24 avertissements hérités (ressources, conventions, ExifInterface et versions Android récentes).
- APK signé vérifié ; affichage renommé Plume TV Chill sans changement de l’identifiant de mise à jour.
- Ajout et retrait automatiques d’une application test vérifiés sur l’appareil ; application test retirée ensuite.
- Icônes natives, fond personnel conservé et navigation D-pad vérifiés sur l’appareil.
- Les APK officiels du verrou ont été téléchargés et inspectés : Zen 2.1.0 min API 24, SmartTube 32.68 min API 17 avec armeabi-v7a, Home on Fire 1.5.2 min API 21. Leurs empreintes SHA-256 sont verrouillées ; ils ne sont pas redistribués ici.
- Installateur execute sur le Stick : lanceur installe, SmartTube/Zen/Home on Fire existants conserves, configuration Home on Fire confirmee et retour Home reel reussi (5,36 s, delai Fire OS inclus). Le telechargement HTTPS de Home on Fire et la verification de son empreinte ont aussi ete testes depuis le script.
- Tests Python : vérification des empreintes et fichiers corrompus, validation des sources HTTPS et du verrou, présence des applications demandées.

Le parcours complet de configuration de Home on Fire est testé sur un Stick où les applications étaient déjà présentes. Le script conserve ces applications et leurs comptes ; ce test ne constitue pas une installation vierge sur tous les modèles de Fire TV. Aucun redémarrage complet, achat, connexion de compte ou essai de lecture vidéo n’est inclus dans cette vérification. La première autorisation ADB reste une action physique sur le téléviseur.
