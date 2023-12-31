#!/bin/sh
# This file is part of Distronode
#
# Distronode is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Distronode is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Distronode.  If not, see <http://www.gnu.org/licenses/>.

if [ -f "$1" ]; then
    . "$1"
else
    echo '{"msg": "No argument file provided", "failed": true}'
    exit 1
fi

salutation=${salutation:=Hello}
name=${name:=World}

cat << EOF
{"msg": "${salutation}, ${name}!"}
EOF
