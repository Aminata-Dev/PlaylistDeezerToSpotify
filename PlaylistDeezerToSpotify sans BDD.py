#P0 :  importations de modules

import requests
#Utilisation de la librairie Spotipy ( #https://github.com/plamere/spotipy / #https://spotipy.readthedocs.io/en/2.16.1/ ) :
import spotipy
from spotipy.oauth2 import SpotifyOAuth
#Pour ouvrir différents liens :
import webbrowser
import json #Permet de convertir des json en dictionnaire python


#P1 : Initialisation des variables, données et fonctions :

id_playlist_deezer = input("Entrez le lien de la playlist Deezer : ( exemple : https://www.deezer.com/fr/playlist/1479458365 ) \n@> ")

try: id_playlist_deezer = id_playlist_deezer[id_playlist_deezer.index("playlist/")+9:] #On récupère l'id du lien en coupant le lien
except ValueError: #Si le lien n'est pas valide, on sort du programme
    print("Le lien n'est pas valide, veuillez recommencer")
    exit()

url_playlist_deezer = f"https://api.deezer.com/playlist/{id_playlist_deezer}" #On restitue le lien avec l'id afin de pouvoir utiliser l'api de deezer
informations_deezer = requests.get(url_playlist_deezer) #On récupère la page

#Si la page affiche un erreur, on sort du programme
if "error" in list(informations_deezer.json().keys()):
    print("Le lien n'est pas valide, veuillez recommencer")
    exit()

liste_uri_spotify_musiques = []
#Initialisation des données du compte spotify :
nom_utilisateur_spotify = input("Quel est votre nom d'utilisateur Spotify : ( https://www.spotify.com/fr/account/overview/?utm_source=play&utm_campaign=wwwredirect > Nom d'utilisateur )\n@> ")
id_client = input("Quel est votre Client ID Spotify ? ( Si c'est la première fois que vous utiliser l'api de Spotify : https://developer.spotify.com/dashboard > Create an app > Create > Edit Settings > dans Redirect URIs mettre http://127.0.0.1:8080/ > Add > Descendre > Save > Client ID // Si vous possedez déjà une app > https://developer.spotify.com/dashboard > Go to your app > Edit Settings > dans Redirect URIs mettre http://127.0.0.1:8080/ > Add > Descendre > Save > Client ID )\n@> ")
mdp_client = input("Quel est votre Client Secret Spotify ? ( https://developer.spotify.com/dashboard/applications > Go to your app > Show Client Secret > Client Secret )\n@> ")
#Ces informations servent à utiliser l'api de Spotify ( voir SpotifyForDevelopers ) par l'intermédiaire de la librairie:
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = id_client,
                                            client_secret = mdp_client,
                                            redirect_uri ="http://127.0.0.1:8080/",
                                            username = nom_utilisateur_spotify,
                                            scope = "playlist-modify-public"))

print("( Si une page web s'ouvre avec 'INVALID_CLIENT: Invalid client', vous n'avez pas saisi les bonnes informations Spotify )\n")

#Fonction permettant de palier aux différents problèmes lors de la recherche de titre et d'artiste sur Spotify ( en créant une nouvelle recherche ) (P2)
def remede_probleme_recherche_spotify():
    global resultats_musiques_spotify
    try:
        resultats_musiques_spotify = sp.search(q=f"{titre[0:titre.index('(')]} {artiste}", limit=1) #Certains titres deezer ont des parenthèses qui ne se trouvent pas dans les titres spotify ( --> l'on coupe alors le titre du début jusqu'a la parenthèse )
    except ValueError: #Si le problème n'était pas ça :
        try:resultats_musiques_spotify = sp.search(q=f"{titre} {artiste[0:artiste.index('&')]}", limit=1) #Dans certains titres, les artistes sont séparés par des '&' sur Deezer, mais pas sur Spotify ( --> l'on coupe alors le nom des artistes du début jusqu'au & )
        except ValueError: #Si le problème n'est toujours pas ça :
            print(f"{'*' * 80}\nLa musique {titre} de {artiste} n'est surement pas sur Spotify\n{'*' * 80}")


#P2 : On récupère l'uri spotify de chaque musique de la playlist deezer :

print(f"Affichage de toutes les musiques de la playlist nommée '{informations_deezer.json()['title']}' : ")
try:
    for i in range(200): #Dans cette boucle :
        artiste = informations_deezer.json()['tracks']['data'][i]['artist']['name'] #On récupère l'information artiste de la playlist dans une variable
        titre = informations_deezer.json()['tracks']['data'][i]['title'] #On récupère l'information titre de la playlist dans une variable
        resultats_musiques_spotify = sp.search(q=f"{titre} {artiste}", limit=1) #On recherche le titre et l'artiste trouvé sur Spotify
        if resultats_musiques_spotify['tracks']['total'] == 0: remede_probleme_recherche_spotify() #Si la recherche n'a rien donné, on utilise la fonction "remede"
        # print(resultats_musiques_spotify) #Affiche le dictionnaire de la recherche
        # print(titre, artiste) #Affiche la recherche menée sur Spotify
        for son in resultats_musiques_spotify['tracks']['items']: #Pour chaque titre trouvé sur Spotify...
            print(f"{i} : {son['name']} - {son['artists'][0]['name']}") #...on affiche le titre et son artiste dans la console
            liste_uri_spotify_musiques.append(son['uri']) #On ajoute l'uri spotify ( identificateur ) de la musique dans une liste
except IndexError: #Si il n'y a plus de musique, on ne fait plus rien
    pass


#P3 : On ajoute les musiques, via leurs uri, dans une playlist spotify :

#Condition permettant de choisir le nom de la nouvelle playlist
choix = input("Souhaitez vous modifier le titre la nouvelle playlist spotify ? ( y --> oui / autre --> non) \n @> ")
if choix == 'y': nom_nouvelle_playlist_spotify = input("Nom de la nouvelle playlist spotify \n @> ")
else:nom_nouvelle_playlist_spotify = informations_deezer.json()['title']

#Condition permettant de couper la liste car la limite est fixée à 100 musiques / requête
if len(liste_uri_spotify_musiques) > 100:
    print("Impossible d'ajouter toutes les musiques : maximum de 100 musiques par requete")
    liste_uri_spotify_musiques = liste_uri_spotify_musiques[0:100]

#Utilisation de la librairie Spotipy
sp.user_playlist_create(user=nom_utilisateur_spotify, name=nom_nouvelle_playlist_spotify, public=True) #On crée la playlist
id_playlist_spotify = sp.user_playlists(user = nom_utilisateur_spotify)['items'][0]['id'] #On récupère l'id de la playlist
sp.user_playlist_add_tracks(user= nom_utilisateur_spotify, playlist_id=id_playlist_spotify, tracks=liste_uri_spotify_musiques) #On ajoute les musiques dans la playlist Spotify par l'intermédiaire de leurs uri

##
webbrowser.open(f"https://www.deezer.com/fr/playlist/{id_playlist_deezer}") #On ouvre la playlist Deezer
webbrowser.open(f"https://open.spotify.com/playlist/{id_playlist_spotify}") #On ouvre la nouvelle playlist Spotify
