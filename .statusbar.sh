#!/bin/bash
#
##
###
#####
######## status-bar-fix.sh

cat > /tmp/check3.py << 'PYEOF'
src = open('/home/lordfingers/ArcaCognitorium/ui/app.py').read()
idx = src.find('status_layer')
print(repr(src[idx:idx+300]))
PYEOF
python3 /tmp/check3.py
