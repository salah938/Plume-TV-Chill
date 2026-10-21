# Plume TV Chill

Un accueil sobre et léger pour Fire TV : grandes tuiles rectangulaires, icônes et couleurs récupérées automatiquement depuis les applications, navigation à la télécommande et couleur des libellés personnalisable.

Fork de [Plume Launcher](https://github.com/aradhyas8/Plume_Launcher), adapté et testé sur Fire TV Stick **AFTSS**, Fire OS 7, Android 9/API 28, **armeabi-v7a**, 1 Go de RAM. Le lanceur fait environ **105 Kio**. Les nouvelles applications utilisateur rejoignent automatiquement l’accueil. Aucun compte ni abonnement n’est fourni.

## Avec Codex ou Cowork

Ouvre ce dépôt dans ton assistant, puis copie cette demande :

> Lis AGENTS.md et installe Plume TV Chill sur mon Fire TV. Installe aussi SmartTube, Zen IPTV Fire OS et Home on Fire avec l’installateur du dépôt. Configure Home on Fire pour ouvrir Plume TV Chill, vérifie le retour avec le bouton Home, puis supprime uniquement les téléchargements temporaires du pack. Demande-moi l’adresse IP du Stick seulement si tu ne peux pas la trouver. Préserve mes comptes, mes réglages et mes autres applications.

L’agent suit `AGENTS.md`, prépare les outils manquants, lance l’installation et vérifie le résultat. La seule étape qui ne peut pas être automatisée depuis l’ordinateur est l’autorisation ADB initiale sur la TV. Si une version de Home on Fire présente une interface différente, l’agent doit inspecter cette interface et terminer la configuration, sans annoncer un succès non vérifié.

## Préparer le Fire TV

1. Dans **Ma Fire TV → À propos**, appuie sept fois sur le nom de l’appareil si les options développeur sont masquées.
2. Active **Débogage ADB** dans les options développeur.
3. Relève l’adresse IP dans les informations réseau.
4. Laisse la TV allumée, et accepte son premier dialogue d’autorisation ADB lorsque l’ordinateur se connecte.

Sur l’ordinateur : Python **3.9+** et [Android Platform Tools (ADB)](https://developer.android.com/tools/releases/platform-tools). Le SDK complet et Android Studio ne sont pas nécessaires pour installer ce pack.

## Une commande

Décompresse le dépôt, ouvre un terminal dans ce dossier et remplace l’adresse ci-dessous :

```sh
python3 scripts/install.py --device IP_DU_FIRE_TV --clean-downloads
```

Sous Windows, `py -3` peut remplacer `python3`. Pour afficher le plan sans toucher au Stick :

```sh
python3 scripts/install.py --dry-run
```

Le script installe le lanceur, télécharge les applications manquantes depuis leurs sources officielles, vérifie leurs empreintes SHA-256, configure Home on Fire et teste un retour par Home. Les applications tierces déjà présentes sont conservées ; ajoute `--update-existing` si tu souhaites les remplacer par les versions du pack. L’installation du lanceur garde ses réglages.

## Applications du pack

| Application | Version du pack | Distribution |
|---|---|---|
| Plume TV Chill | 1.4.0 | APK inclus dans `dist/`, sources dans ce dépôt |
| [SmartTube](https://github.com/yuliskov/SmartTube) | 32.68 stable, ARM 32 bits | Téléchargement officiel à l’installation |
| [Zen IPTV](https://zeniptv.app/android) | 2.1.0 Fire OS | [APK Fire OS officiel](https://zeniptv.app/releases/zeniptv_fireos.apk), téléchargé à l’installation |
| [Home on Fire](https://github.com/toolicious/home-on-fire) | 1.5.2 | Téléchargement officiel à l’installation |

Prévois environ **155 Mo de téléchargements** si aucune application n’est encore présente, principalement pour Zen. `--clean-downloads` enlève ensuite ce cache de l’ordinateur. Les applications elles-mêmes restent installées sur le Stick.

Les versions et empreintes sont enregistrées dans `apps.lock.json`. Si un éditeur remplace un APK à une adresse existante, le script refuse une empreinte différente : il faut vérifier le nouveau fichier avant de mettre à jour le verrou. Aucun APK tiers n’est republié dans ce dépôt.

**Netflix et Crunchyroll** s’installent depuis l’Amazon Appstore avec le compte du destinataire. **IBO Player** existe en plusieurs éditions : utilise le téléchargement officiel de l’édition souhaitée ou un APK local dont tu disposes. Ces trois APK ne sont pas inclus dans le pack. Chaque personne configure ses propres comptes, abonnements et sources de lecture.

Pour ajouter un APK local à l’installation :

```sh
python3 scripts/install.py --device IP_DU_FIRE_TV --apk /chemin/application.apk --clean-downloads
```

Les APK locaux ne doivent pas être ajoutés au dépôt. `optional-apks/` est ignoré par Git pour cet usage.

## Home et performances

La configuration automatique active le service Home on Fire, sélectionne **Plume TV Chill**, active le lancement au démarrage et utilise un écran noir de transition sur Fire OS 7. Elle conserve les autres services d’accessibilité.

Fire OS 7 peut imposer jusqu’à environ cinq secondes de délai système au bouton Home. Un écran noir masque l’attente, il ne l’annule pas. Une touche libre peut servir de raccourci via Home on Fire ; aucune touche supplémentaire n’est réaffectée par le script.

Le rapport local `.logs/install-report.json` doit contenir `home_verified: true` pour que le retour Home soit considéré comme vérifié. Les captures de structure d’interface utiles au diagnostic restent dans `.logs/`, qui n’est pas publié.

## Personnalisation

Dans les réglages du lanceur : **Couleur du texte** propose une palette et un code `#RRGGBB`. Un appui long sur une tuile permet de la déplacer ou de la retirer de l’accueil ; elle reste accessible dans la grille de toutes les applications. Les icônes ne sont ni téléchargées ni définies à la main.

Les fonds personnels se choisissent dans les réglages. Aucun fond, identifiant, abonnement, playlist ou compte de l’auteur n’est partagé. Le fond est affiché en 720p pour limiter la RAM. L’application n’effectue pas de vérification automatique de mise à jour de l’upstream.

## Nettoyage limité

La demande de partage ne comprend aucune suppression de composant Amazon. Le nettoyage par défaut enlève seulement les téléchargements du pack :

```sh
python3 scripts/cleanup.py
python3 scripts/cleanup.py --apply
```

L’ancienne application `dev.plume` peut être retirée **si son utilisateur le demande**. Le script exige que le nouveau lanceur soit installé et que le retour Home fonctionne avant de la supprimer. Les photos de son dossier de fonds sont copiées vers le nouveau dossier si elles existent, mais ses anciens réglages privés sont supprimés avec l’application :

```sh
python3 scripts/cleanup.py --device IP_DU_FIRE_TV --remove-old-plume
python3 scripts/cleanup.py --device IP_DU_FIRE_TV --remove-old-plume --apply
```

Aucune commande ne désinstalle les applications Amazon, Netflix, Crunchyroll, IBO, SmartTube ou Zen.

## Développement et mises à jour

L’identifiant technique reste `dev.plume.salah` pour que les installations existantes puissent être mises à jour sans perdre leurs réglages ; le nom affiché est **Plume TV Chill**. La version du dépôt conserve l’API minimale 26, sans bibliothèque native ni dépendance d’interface externe.

Pour compiler : JDK 21, SDK Android 36, Build Tools 36.0.0 et `ANDROID_HOME` configuré :

```sh
./gradlew testDebugUnitTest assembleRelease lintRelease
python3 -m unittest discover -s tests -v
```

L’APK dans `dist/` est signé avec la clé locale ayant servi à ses versions précédentes. Une compilation sur un autre ordinateur ou dans CI utilise une autre clé par défaut et ne remplace pas directement cette installation. Conserve une clé stable pour publier tes futures mises à jour ; les clés ne doivent jamais être commitées. Le workflow CI vérifie le build et les tests, sans publier automatiquement un APK de signature différente.

## Licence et attribution

Lanceur et modifications : **GPL-3.0**, voir [LICENSE](LICENSE). Base : [aradhyas8/Plume_Launcher](https://github.com/aradhyas8/Plume_Launcher), commit `3c439a0d300b1241494a56e09cffaba120027978`. Les auteurs et licences des ressources du projet d’origine sont conservés.

SmartTube, Zen et Home on Fire sont des projets indépendants distribués par leurs éditeurs, avec leurs propres licences et conditions. Ce dépôt n’est pas affilié à Amazon, Apple, Netflix, Crunchyroll, SmartTube, Zen ou IBO Player.
