# pyOpenGL-Test
 Impariamo ad usare pyOpenGL step by step

1. scaricare python e il gestore di git "GitHub Desktop" dai rispettivi siti web

2. Cloniamo il repository da github del corso

3. creare il virtual environment:
python -m venv venv

4. attivare il venv:
.\venv\Scripts\activate.bat
(per disattivarlo: deactivate )

5. Aggiornare pip con:
python -m pip install --upgrade pip

6. Per vedere i pacchetti installati:
pip list

7. Scaricare le librerie necessarie manualmente (oppure utilizzando il punto 9):
installare pygame, numpy, pyglet e pywavefront (e le altre librerie necessarie)
Dal sito https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyopengl prendere le librerie
PyOpenGL e PyOpenGL_accelerate (cpXX indica la versione di python, e scegliere la versione a 32 o 64 bit in accordo con la versione di python, da vedere con python --version )

8. Una volta installate tutte le librerie, documentare il progetto con:
pip freeze > requirements.txt

9. Per ripristinarlo:
pip install -r requirements.txt

10. Per i modelli usare: https://archive3d.net/