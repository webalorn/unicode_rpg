cd rpg
python3 -m cProfile -o main.prof main.py
snakeviz main.prof