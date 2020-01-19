cd rpg
pypy3 main.py "$@" 2> err_main.log
cd ..
mkdir -p log
mv rpg/err_main.log log/err_main.log
mv rpg/error.log log/error.log
mv rpg/debug.log log/debug.log
cd log
cat err_main.log
cat error.log
cat debug.log