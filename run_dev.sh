rm -R log 2>/dev/null
mkdir -p log
python3 rpg/main.py "$@" 2> log/err_main.log

mv rpg/log/*.log log
cat log/*.log