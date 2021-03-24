# Vaatismusmäärittely
## Sovelluksen tarkoitus
Sovelluksessa 4 käyttäjää pystyy pelaamaan vastakkain Chicago-korttipeliä. Chicagossa pelataan aluksi 2 kierrosta pokeria ja kierros päätetään tikkiin. Kummankin pokerikierroksen jälkeen pelaajan on mahdollista vaihtaa enintään 4 korttia. Wikipedia: https://fi.wikipedia.org/wiki/Chicago_(korttipeli)
## Käyttöliittymä
Sovelluksessa käytetään graafista käyttöliittymää. Alussa pyydetään pelaajien nimet. Nimien syöton jälkeen avautuu peliruutu, jossa keskellä näyttöä näkyy pakka ja jokaisella sivulla pelaajien kortit. Vuorossa olevan pelaajan kortit näkyvät oikein päin, muiden väärin päin. Peliruudun sivulla näkyy pistetaulukko.
## Toiminnallisuus
Sovelluksessa pidetään kirjaa tuloksista ja voittaja on pelaaja, joka pääsee ensimmäisenä 52 pisteeseen. Pelissä on mahdollista pokerikierroksen jälkeen huutaa chicago, jolloin kyseinen pelaaja aloittaa tikkivuoron ja hänen tulee voittaa jokainen tikkikäsi. Chicagon lisäksi pelaajan on mahdollista huutaa blanco-chicago ennen viimeistä vaihtoa, jolloin kyseisen pelaajan tulee vaihtaa vähintään yksi kortti ja tämän jälkeen onnistua normaalissa chicagossa. Jokaisen kierroksen (paitsi chicago-kierroksen) jälkeen lopussa tarkistetaan vielä pokerikäsi, ja paras käsi saa pisteet.
Pisteytys:
Pari: 1p
Kaksi paria: 2p
Kolmoset: 3p
Suora: 4p
Väri: 5p
Täyskäsi: 6p
Neloset: 8p (ja kaikki muut pelaajat tippuvat 0 pisteeseen)
Värisuora: peli loppuu ja kyseinen pelaaja voittaa
Tikin lopetus: 5p
Tikin lopetus kakkosella: 10p
Chicago (onnistunut/epäonnistunut): 15/-15
Blanco-chicago (onnistunut/epäonnistunu): 30/-30