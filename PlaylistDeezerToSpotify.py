print("\n***\nWelcome ! This program allows the migration of Deezer playlist into Spotify playlist. The instructions are in English, but the comments are in French : don't hesitate to ask questions on the Github in case of misunderstanding. In order to test the code, I have made my account available. So there is no need to connect to your Spotify account.\n***\n")

#P0 :  importations de modules

import requests
#Utilisation de la librairie Spotipy ( #https://github.com/plamere/spotipy / #https://spotipy.readthedocs.io/en/2.16.1/ ) :
import spotipy
from spotipy.oauth2 import SpotifyOAuth
#Pour ouvrir différents liens :
import webbrowser
import json #Permet de convertir des json en dictionnaire python
import time #afin de laisser du temps entre deux requêtes si la longueur de la playlist est supérieur à 100
import os #pour verifier si le fichier texte contenant les informations spotify existe et supprimer le fichier contenant les informations


#P1 : Initialisation des variables, données et fonctions :

id_playlist_deezer = input("Enter the link of the deezer : ( example : https://www.deezer.com/fr/playlist/1479458365 or https://www.deezer.com/en/playlist/5782150322?utm_campaign=clipboard-generic ) \n@> ")

try: id_playlist_deezer = id_playlist_deezer[id_playlist_deezer.index("playlist/")+9:] #On récupère l'id du lien en coupant le lien
except ValueError: #Si le lien n'est pas valide, on sort du programme
    print("The link is not valid, please try again")
    exit()

#le lien de playlist Deezer que l'utilisateur entre est parfois accompagné de "?utm_campaign=clipboard-generic&..." après l'id. On essaye de voir si c'est le cas et de couper à partir du point d'intérrogation pour ne récupérer que l'id
try: id_playlist_deezer = id_playlist_deezer[:id_playlist_deezer.index('?')]
except ValueError: pass

url_playlist_deezer = f"https://api.deezer.com/playlist/{id_playlist_deezer}" #On restitue le lien avec l'id afin de pouvoir utiliser l'api de deezer
informations_deezer = requests.get(url_playlist_deezer) #On récupère la page contenant les informations générales de la playlist afin d'utiliser le titre de la playlist
informations_deezer_tracks = requests.get(f"{url_playlist_deezer}/tracks") #On récupère la page

#Si la page affiche une erreur, on sort du programme
if "error" in list(informations_deezer.json().keys()):
    print("The link is not valid, please try again")
    exit()

def ecriture_informations_fichier_texte(nom, id_, mdp):
    if os.path.exists("informations_spotify_accounts_in_order_to_automate_the_process.txt"): #Si le fichier contenant les informations existe...
        os.remove("informations_spotify_accounts_in_order_to_automate_the_process.txt") #... on supprime le ficher
    #systeme de stockage des informations en local sur un fichier texte afin de ne pas avoir à retaper toutes les informations à chaque lancement du code
    with open("informations_spotify_accounts_in_order_to_automate_the_process.txt", 'w') as fichier: #creation du fichier texte
        for i in nom, id_, mdp:
            fichier.write(f"{i}\n")

liste_uri_spotify_musiques = []
liste_musique_pas_trouve = []
demande_remplissage_automatique = 'n'

if os.path.exists('informations_spotify_accounts_in_order_to_automate_the_process.txt'): #Si le fichier contenant les informations existe...
    demande_remplissage_automatique = input("\nInformations that you have entered previously has been found. Would you like to enter your Spotify username, Spotify Client ID and your Spotify Client Secret automatically ? ( y --> yes / other --> no )\n@> ") #...on demande à l'utilisateur s'il veut les rentrer automatiquement
    if demande_remplissage_automatique == 'y': #Si une demande de remplissage auto est demandée, on vient lire le fichier
        with open('informations_spotify_accounts_in_order_to_automate_the_process.txt', 'r') as fichier:
            lignes_fichier = fichier.read()
            #car avec la méthode readlines, chaque str etait precede d'un \n, ce qui creait des conflit car il etait "invisible" :
            nom_utilisateur_spotify, id_client, mdp_client = lignes_fichier.split('\n')[0], lignes_fichier.split('\n')[1], lignes_fichier.split('\n')[2]
if demande_remplissage_automatique != 'y': #Si l'utilisateur ne veut pas entrer ces informations automatiquement
    #Initialisation des données du compte spotify :
    nom_utilisateur_spotify = input("\nWhat is your Spotify username ? : ( https://www.spotify.com/ca-en/account/overview/?utm_source=play&utm_campaign=wwwredirect > Copy/Past Username )\n( You can use arghp85zv4fr9lieuyv1azqe5 to test the code )\n@> ")
    id_client = input("\nWhat is your Spotify Client ID ?\n --> If this is the first time you use the Spotify API : https://developer.spotify.com/dashboard > Create an app > Create > Edit Settings > in Redirect URIs put http://127.0.0.1:8080/ > Add > Go down > Save > Copy/Past Client ID\n --> If you already get an app > https://developer.spotify.com/dashboard > Go to your app > Edit Settings > in Redirect URIs put http://127.0.0.1:8080/ > Add > Go down > Save > Copy/Past Client ID )\n( You can use 3e4adb55d5a44652baf952503c1148a8 to test the code )\n@> ")
    mdp_client = input("\nWhat is your Spotify Client Secret ? ( https://developer.spotify.com/dashboard/applications > Go to your app > Show Client Secret > Copy/Past Client Secret )\n( You can use 9ca44fc7732b4f1ea25cc66da1fc4d01 to test the code )\n@> ")
    ecriture_informations_fichier_texte(nom_utilisateur_spotify, id_client, mdp_client)

try: #Si les informations ne sont pas bonnes
    #Ces informations servent à utiliser l'api de Spotify ( voir SpotifyForDevelopers ) par l'intermédiaire de la librairie:
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = id_client,
                                                client_secret = mdp_client,
                                                redirect_uri ="http://127.0.0.1:8080/",
                                                username = nom_utilisateur_spotify,
                                                scope = "playlist-modify-public"))
except:
    print("\nPlease try again. It should work.")

print("\n( IF A WEB PAGE OPENS WITH 'INVALID_CLIENT: Invalid client' in, YOU DID NOT ENTER THE CORRECT SPOTIFY INFORMATIONS ( CHECK THE SPACES WHEN YOU ENTER THE DIFFERENT INFORMATIONS ) )\n")

#Fonction permettant de palier aux différents problèmes lors de la recherche de titre et d'artiste sur Spotify ( en créant une nouvelle recherche ) (P2)
def remede_probleme_recherche_spotify():
    global resultats_musiques_spotify
    try:
        resultats_musiques_spotify = sp.search(q=f"{titre[0:titre.index('(')]} {artiste}", limit=1) #Certains titres deezer ont des parenthèses qui ne se trouvent pas dans les titres spotify ( --> l'on coupe alors le titre du début jusqu'a la parenthèse )
    except ValueError: #Si le problème n'était pas ça :
        try:resultats_musiques_spotify = sp.search(q=f"{titre} {artiste[0:artiste.index('&')]}", limit=1) #Dans certains titres, les artistes sont séparés par des '&' sur Deezer, mais pas sur Spotify ( --> l'on coupe alors le nom des artistes du début jusqu'au & )
        except ValueError: #Si le problème n'est toujours pas ça :
            print(f"{'*' * 80}\nThe song {titre} of {artiste} is certainly not on Spotify\n{'*' * 80}")
            liste_musique_pas_trouve.append(f"{titre} - {artiste}")


#P2 : On récupère l'uri spotify de chaque musique de la playlist deezer :

print(f"Display of all the songs in the playlist named '{informations_deezer.json()['title']}' : ")
try:
    compteur = 0 #compteur allant de 0 à 24, servant à indexer correctement chaque son d'un page
    for i in range(informations_deezer_tracks.json()['total']): #Dans cette boucle :
        artiste = informations_deezer_tracks.json()['data'][compteur]['artist']['name'] #On récupère l'information artiste de la playlist dans une variable
        titre = informations_deezer_tracks.json()['data'][compteur]['title'] #On récupère l'information titre de la playlist dans une variable
        resultats_musiques_spotify = sp.search(q=f"{titre} {artiste}", limit=1) #On recherche le titre et l'artiste trouvé sur Spotify
        if resultats_musiques_spotify['tracks']['total'] == 0: remede_probleme_recherche_spotify() #Si la recherche n'a rien donné, on utilise la fonction "remede"
        # print(resultats_musiques_spotify) #Affiche le dictionnaire de la recherche
        # print(titre, artiste) #Affiche la recherche menée sur Spotify
        compteur += 1
        for son in resultats_musiques_spotify['tracks']['items']: #Pour chaque titre trouvé sur Spotify...
            print(f"{i + 1} : {son['name']} - {son['artists'][0]['name']}") #...on affiche le titre et son artiste dans la console ( i + 1 pour commencer à 1 )
            liste_uri_spotify_musiques.append(son['uri']) #On ajoute l'uri spotify ( identificateur ) de la musique dans une liste
        if compteur in [j for j in range(25, informations_deezer_tracks.json()['total'], 25)]: #le json affiche 25 sons sur une page, et les 25 autres sur l'autre page. Si nous avons parcouru les 25 sons de la page...
            try:
                informations_deezer_tracks = requests.get(f"{informations_deezer_tracks.json()['next']}/tracks") #... on modifie la variable contenant les infos
                compteur = 0
            except KeyError: pass #Si il n'y a pas / plus de next
except: #Si il n'y a plus de musique, on ne fait plus rien
    for fichier in os.listdir("."): #Le fichier cache crée des conflits
        if fichier[0:7] == ".cache-":
            os.remove(fichier)
    print("\nPlease try again. It should work.")
    try: os.remove("informations_spotify_accounts_in_order_to_automate_the_process.txt") #si les infos ne sont pas bonnes, on les supprime
    except: pass
    exit()


#P3 : On ajoute les musiques, via leurs uri, dans une playlist spotify :

#Condition permettant de choisir le nom de la nouvelle playlist
choix = input("Would you like to change the name of the new Spotify playlist ? ( y --> yes / other --> no )\n@> ")
if choix == 'y': nom_nouvelle_playlist_spotify = input("Name of the new Spotify playlist\n@> ")
else:nom_nouvelle_playlist_spotify = informations_deezer.json()['title']

#Utilisation de la librairie Spotipy :
sp.user_playlist_create(user=nom_utilisateur_spotify, name=nom_nouvelle_playlist_spotify, public=True) #On crée la playlist
def alimentation_playlist_spotify(arg_liste_uri_spotify_musiques):
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
# webbrowser.open(f"https://www.deezer.com/fr/playlist/{id_playlist_deezer}") #On ouvre la playlist Deezer
print("\nDone")
webbrowser.open(f"https://open.spotify.com/playlist/{id_playlist_spotify}") #On ouvre la nouvelle playlist Spotify

if len(liste_musique_pas_trouve) != 0:
    print(f"\nSongs not found :\n{liste_musique_pas_trouve}\nNormally, these songs are not on Spotify. But you can always try to find them. If you find them, don't hesitate to show me on Github, I'll fix the code")

if len(liste_musique_pas_trouve) != 0:
    print(f"\nSongs not found :\n{liste_musique_pas_trouve}\nNormally, these songs are not on Spotify. But you can always try to find them. If you find them, don't hesitate to show me on Github, I'll fix the code")
