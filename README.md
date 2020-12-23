# PlaylistDeezerToSpotify
Permet la migration de playlist Deezer à Spotify ( pas besoin d'abonnement )

Attention:
- Si c'est la première fois que vous lancez le code, vous serez peut-être ammenés à accepter une autorisation Spotify sur une page web. Après l'avoir accepté, relancer le code.

Prérequis : 
- installer le module spotipy. Sur windows : 
```py
pip install spotipy
```
- installer le module requests. Sur windows : 
```py
pip install requests
```
- installer le module webbrowser. Sur windows : 
```py
pip install webbrowser
```
- Pour le code avec la base de donnée : installer le module mysql-connector-python ( sur windows : 
```py
pip install mysql-connector-python
```
 ), puis installer Xampp ( https://www.apachefriends.org/fr/index.html ) + start Apache et MySQL
 
 Demonstration :
 
 S'assurer d'avoir entrer les bonnes informations :
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/1.png)
 
 Dans la console s'affiche tous les titres :
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/2.PNG)
 
 Choisir un nom de playlist ( pour obtenir le même nom que la playlist deezer, laisser vide ) :
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/3.PNG)
 
 Deux liens s'ouvrent ( pour la partie sans BDD ). On retrouve la playlist Deezer originale et la nouvelle playlist Spotify :
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/4.png)
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/5.PNG)
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/6.png)
 
 Une troisième page s'ouvre pour la partie BDD; avec deux tables dedans :
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/7.PNG)
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/8.PNG)
 ![1](https://github.com/Aminata-Dev/PlaylistDeezerToSpotify/blob/main/Screenshots/9.PNG)
