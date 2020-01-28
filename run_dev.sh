rm -R log 2>/dev/null
cd rpg
python3 main.py "$@" 2> err_main.log
cd ..

mkdir -p log
mv rpg/*.log log
cat log/*.log