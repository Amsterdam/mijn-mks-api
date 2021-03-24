MKS (Makelaars suite)
---------------------

Wat?
====
Makelaarssuite is een interne applicatie van de gemeente waar informatie uit zowel de BRP (Basisregistratie Persoonsgegevens)
als het HR (Handelsregister c.q. Kamer van Koophandel) is te vinden.

Op dit moment wordt alleen de BRP ontsloten


Hoe?
====
Bij het starten van de applicatie dient het pubieke certificaat van de TMA (Toegangsmakelaar Amsterdam) te worden gegeven
De TMA is een SIAM (Secure Identity and Access Management) provider welke centraal authenticatie biedt voor de hele gemeente
door middel van de TMA is Digid, eHerkenning maar ook username/password authenticatie voor ambtenaren bij de gemeente
mogelijk.

Deze applicatie wordt door gebruikers indirect benaderd. TMA fungeert als reverse proxy en injecteerd een SAML token in
de requests die worden doorgestuurd vanaf de gebruiker. In dit token zit het BSN van de gebruiker alsmede een digitale
handtekening. Mks controleert de handtekening, extraheert het BSN en bevraagd de MKS met dit BSN. Er worden geen andere
input parameters behalve het SAML token verwerkt.

Wat levert de MKS precies?
==========================
MKS antwoord in StUF (Standaard Uitwisselingsformaat). Deze standaard van alles beschrijft alles over alles in een
standaard formaat. Dat is bijna net zo nuttig als het klinkt en derhalve is de interface breekbaar bij veranderingen
in de MKS. In het geval van een bevraging met BSN van de BRP wordt een antwoord samengesteld waarin alle beschikbare
informatie over de onderhavige persoon, diens nationaliteit(en), partner, ouders en kinderen uit de brp worden geretourneerd.
Velden die niet toegankelijk zijn om welke rede ook (niet beschikbaar, geen authorisatie, onbekend etc.) worden uit het
resultaat weggelaten.
Een Swagger definitie is in de root van het project te vinden.


Ontwikkeling:
-------------


Running tests
=============
* activate virtual env
* :code:`python -m unittest`

There are test targets in the make file, I (Johan) could not get them to work.


Updating dependencies
=====================
Direct dependencies are specified in `requirements-root.txt`. These should not have pinned a version (except when needed)

* ``pip install -r requirements-root.txt``
* ``pip freeze > requirements.txt``


