print("Welcome ! This program allows the migration of Deezer playlist into Spotify playlist. The instructions are in English, but the comments are in French : don't hesitate to ask questions on the Github in case of misunderstanding :)\n")

#P0 :  importations de modules

import requests
#Utilisation de la librairie Spotipy ( #https://github.com/plamere/spotipy / #https://spotipy.readthedocs.io/en/2.16.1/ ) :
import spotipy
from spotipy.oauth2 import SpotifyOAuth
#Pour ouvrir différents liens :
import webbrowser
import json #Permet de convertir des json en dictionnaire python
import mysql.connector #Creation base de donnée ( BDD )
import time #afin de laisser du temps entre deux requêtes si la longueur de la playlist est supérieur à 100
import os #pour travailler depuis cmd dans python et pour verifier si le fichier texte contenant les informations spotify existe

os.system(r"c: && cd C:\xampp && xampp_start") #On lance xampp depuis la console à l'aide d'une commande cmd

#P1 : Initialisation des variables, données et fonctions :

#Partie BDD :
#On crée une nouvelle base de donnée si elle n'existe pas :
connection = mysql.connector.connect(host='localhost',database='',user='root',password='')
curseur = connection.cursor()
requete_creation_bdd = "CREATE DATABASE IF NOT EXISTS PLAYLISTDEEZERTOSPOTIFY"
curseur.execute(requete_creation_bdd)
connection.close()
#On refait une connection en spécifiant cette fois la base de donnée afin d'y effectuer des actions :
connection = mysql.connector.connect(host='localhost',database='PLAYLISTDEEZERTOSPOTIFY',user='root',password='')
curseur = connection.cursor()
curseur.execute("CREATE TABLE IF NOT EXISTS `INFO_PLAYLIST_DEEZER` ( `id` INT PRIMARY KEY NOT NULL AUTO_INCREMENT, `titre_musique` VARCHAR(255) NOT NULL , `titre_raccourci_musique` VARCHAR(255) NOT NULL , `lien_musique` VARCHAR(255) NOT NULL , `duree_musique` INT NOT NULL, `classement_musique` INT NOT NULL, `artiste` VARCHAR(255) NOT NULL,`album_musique` VARCHAR(255) NOT NULL) ENGINE = InnoDB;")
curseur.execute("TRUNCATE `info_playlist_deezer`") #On vide la table ( au cas où elle existe déjà )
curseur.execute("CREATE TABLE IF NOT EXISTS `INFO_PLAYLIST_SPOTIFY` ( `id_musique_deezer` INT PRIMARY KEY NOT NULL AUTO_INCREMENT, `lien_album` VARCHAR(255) NOT NULL, `url_musique` VARCHAR(255) NOT NULL) ENGINE = InnoDB;")
curseur.execute("TRUNCATE `info_playlist_spotify`") #On vide la table ( au cas où elle existe déjà )
connection.commit() #On soumet la requete


id_playlist_deezer = input("Enter the link of the deezer : ( example : https://www.deezer.com/fr/playlist/1479458365 ) \n@> ")

try: id_playlist_deezer = id_playlist_deezer[id_playlist_deezer.index("playlist/")+9:] #On récupère l'id du lien en coupant le lien
except ValueError: #Si le lien n'est pas valide, on sort du programme
    print("The link is not valid, please try again")
    exit()

url_playlist_deezer = f"https://api.deezer.com/playlist/{id_playlist_deezer}" #On restitue le lien avec l'id afin de pouvoir utiliser l'api de deezer
informations_deezer = requests.get(url_playlist_deezer) #On récupère la page

#Si la page affiche un erreur, on sort du programme
if "error" in list(informations_deezer.json().keys()):
    print("The link is not valid, please try again")
    exit()

def ecriture_informations_fichier_texte(nom, id_, mdp):
    #systeme de stockage des informations en local sur un fichier texte afin de ne pas avoir à retaper toutes les informations à chaque lancement du code
    with open('informations_spotify_accounts_in_order_to_automate_the_process.txt', 'w') as fichier:
        for i in nom, id_, mdp:
            fichier.write(i + '\n')

liste_uri_spotify_musiques = []

if os.path.exists('informations_spotify_accounts_in_order_to_automate_the_process.txt'): #Si le fichier contenant les informations existe...
    demande_remplissage_automatique = input("\nInformations that you have entered previously has been found. Would you like to enter your Spotify username, Spotify Client ID and your Spotify Client Secret automatically ? ( y --> yes / other --> no ) \n @> ") #...on demande à l'utilisateur s'il veut les rentrer automatiquement
    if demande_remplissage_automatique == 'y': #Si une demande de remplissage auto est demandée, on vient lire le fichier
        with open('informations_spotify_accounts_in_order_to_automate_the_process.txt', 'r') as fichier:
            lignes_fichier = fichier.readlines()
            nom_utilisateur_spotify, id_client, mdp_client = lignes_fichier
            print(nom_utilisateur_spotify, id_client, mdp_client)
else:
    #Initialisation des données du compte spotify :
    nom_utilisateur_spotify = input("\nWhat is your Spotify username ? : ( https://www.spotify.com/ca-en/account/overview/?utm_source=play&utm_campaign=wwwredirect > Copy/Past Username )\n@> ")
    id_client = input("\nWhat is your Spotify Client ID ?\n --> If this is the first time you use the Spotify API : https://developer.spotify.com/dashboard > Create an app > Create > Edit Settings > in Redirect URIs put http://127.0.0.1:8080/ > Add > Go down > Save > Copy/Past Client ID\n --> If you already get an app > https://developer.spotify.com/dashboard > Go to your app > Edit Settings > in Redirect URIs put http://127.0.0.1:8080/ > Add > Go down > Save > Copy/Past Client ID )\n@> ")
    mdp_client = input("\nWhat is your Spotify Client Secret ? ( https://developer.spotify.com/dashboard/applications > Go to your app > Show Client Secret > Copy/Past Client Secret )\n@> ")
    ecriture_informations_fichier_texte(nom_utilisateur_spotify, id_client, mdp_client)

#Ces informations servent à utiliser l'api de Spotify ( voir SpotifyForDevelopers ) par l'intermédiaire de la librairie:
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = id_client,
                                            client_secret = mdp_client,
                                            redirect_uri ="http://127.0.0.1:8080/",
                                            username = nom_utilisateur_spotify,
                                            scope = "playlist-modify-public"))

print("\n( IF A WEB PAGE OPENS WITH 'INVALID_CLIENT: Invalid client' in, YOU DID NOT ENTER THE CORRECT SPOTIFY INFORMATIONS (CHECK THE SPACES WHEN YOU ENTER THE DIFFERENT INFORMATIONS) )\n")

#Fonctions de creations de requetes SQL ( P2 )
def f_requete_ajout_deezer():
    return "INSERT INTO `info_playlist_deezer` (`id`, `titre_musique`, `titre_raccourci_musique`, `lien_musique`, `duree_musique`, `classement_musique`, `artiste`, `album_musique`) VALUES (NULL,'%s','%s','%s','%s','%s','%s','%s')" % (
        informations['title'].replace('\'','\\\''),
        informations['title_short'].replace('\'','\\\''),
        informations['link'],
        informations['duration'],
        informations['rank'],
        informations['artist']['name'].replace('\'','\\\''),
        informations['album']['title'].replace('\'','\\\'')
                                                                                )

def f_requete_ajout_spotify():
    return f"INSERT INTO `INFO_PLAYLIST_SPOTIFY` ( `id_musique_deezer`, `lien_album`, `url_musique`) VALUES (NULL,'https://open.spotify.com/album/{son['album']['id']}', '{son['external_urls']['spotify']}')"

#Fonction permettant de palier aux différents problèmes lors de la recherche de titre et d'artiste sur Spotify ( en créant une nouvelle recherche ) (P2)
def remede_probleme_recherche_spotify():
    global resultats_musiques_spotify
    try:
        resultats_musiques_spotify = sp.search(q=f"{titre[0:titre.index('(')]} {artiste}", limit=1) #Certains titres deezer ont des parenthèses qui ne se trouvent pas dans les titres spotify ( --> l'on coupe alors le titre du début jusqu'a la parenthèse )
    except ValueError: #Si le problème n'était pas ça :
        try:resultats_musiques_spotify = sp.search(q=f"{titre} {artiste[0:artiste.index('&')]}", limit=1) #Dans certains titres, les artistes sont séparés par des '&' sur Deezer, mais pas sur Spotify ( --> l'on coupe alors le nom des artistes du début jusqu'au & )
        except ValueError: #Si le problème n'est toujours pas ça :
            print(f"{'*' * 80}\nThe song {titre} of {artiste} is certainly not on Spotify\n{'*' * 80}")


#P2 : On récupère l'uri spotify de chaque musique de la playlist deezer :

print(f"Display of all the songs in the playlist named '{informations_deezer.json()['title']}' : ")
try:
    for i in range(200): #Dans cette boucle :
        artiste = informations_deezer.json()['tracks']['data'][i]['artist']['name'] #On récupère l'information artiste de la playlist dans une variable
        titre = informations_deezer.json()['tracks']['data'][i]['title'] #On récupère l'information titre de la playlist dans une variable
        resultats_musiques_spotify = sp.search(q=f"{titre} {artiste}", limit=1) #On recherche le titre et l'artiste trouvé sur Spotify
        if resultats_musiques_spotify['tracks']['total'] == 0: remede_probleme_recherche_spotify() #Si la recherche n'a rien donné, on utilise la fonction "remede"
        # print(resultats_musiques_spotify) #Affiche le dictionnaire de la recherche
        # print(titre, artiste) #Affiche la recherche menée sur Spotify
        for son in resultats_musiques_spotify['tracks']['items']: #Pour chaque titre trouvé sur Spotify...
            print(f"{i + 1} : {son['name']} - {son['artists'][0]['name']}") #...on affiche le titre et son artiste dans la console ( i + 1 pour commencer à 1 )
            liste_uri_spotify_musiques.append(son['uri']) #On ajoute l'uri spotify ( identificateur ) de la musique dans une liste
            requete_ajout_spotify = f_requete_ajout_spotify() #On crée une requete SQL
            curseur.execute(requete_ajout_spotify) #On execute la requete SQL
        informations = informations_deezer.json()['tracks']['data'][i] #Pour la ligne suivante
        requete_ajout_deezer = f_requete_ajout_deezer() #On crée une requete SQL
        # print(f"Requete : {requete_ajout_deezer}") #Affiche la requête
        curseur.execute(requete_ajout_deezer) #On execute la requete SQL
        connection.commit() #On soumet les requetes
except IndexError: #Si il n'y a plus de musique, on ne fait plus rien
    pass


#P3 : On ajoute les musiques, via leurs uri, dans une playlist spotify :

#Condition permettant de choisir le nom de la nouvelle playlist
choix = input("Would you like to change the name of the new Spotify playlist ? ( y --> yes / other --> no ) \n @> ")
if choix == 'y': nom_nouvelle_playlist_spotify = input("Name of the new Spotify playlist \n @> ")
else:nom_nouvelle_playlist_spotify = informations_deezer.json()['title']

def alimentation_playlist_spotify(arg_liste_uri_spotify_musiques):
    #Utilisation de la librairie Spotipy
    sp.user_playlist_create(user=nom_utilisateur_spotify, name=nom_nouvelle_playlist_spotify, public=True) #On crée la playlist
    global id_playlist_spotify #on passe la variable en global afin de la réutiliser dans le lien
    id_playlist_spotify = sp.user_playlists(user = nom_utilisateur_spotify)['items'][0]['id'] #On récupère l'id de la playlist
    sp.user_playlist_add_tracks(user= nom_utilisateur_spotify, playlist_id=id_playlist_spotify, tracks=arg_liste_uri_spotify_musiques) #On ajoute les musiques dans la playlist Spotify par l'intermédiaire de leurs uri

if len(liste_uri_spotify_musiques) > 100:
    #algorithme permettant de faire les requêtes progressivement car la limite est fixée à 100 musiques / requête :
    while liste_uri_spotify_musiques != []:
        alimentation_playlist_spotify(liste_uri_spotify_musiques[0: 100]) #On appelle la fonction avec les 100 premiers éléments de la liste...
        liste_uri_spotify_musiques = liste_uri_spotify_musiques[100: len(liste_uri_spotify_musiques)] #... et on coupe la liste du 100eme element à la longueur de la liste
        print("Please wait...")
        time.sleep(3)
else:
    alimentation_playlist_spotify(liste_uri_spotify_musiques)

##
webbrowser.open("http://localhost/phpmyadmin/db_structure.php?server=1&db=playlistdeezertospotify") #On ouvre la BDD
# webbrowser.open(f"https://www.deezer.com/fr/playlist/{id_playlist_deezer}") #On ouvre la playlist Deezer
webbrowser.open(f"https://open.spotify.com/playlist/{id_playlist_spotify}") #On ouvre la nouvelle playlist Spotify
