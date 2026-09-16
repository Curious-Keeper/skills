#!/usr/bin/env bash
# Append one row to a decision trail (see ../SKILL.md).
#
#   log.sh <logfile> <phase> <decision> <why> <evidence> <result>
#
# Stamps ts, writes the header on first use, and normalises each cell so one
# row stays one row. Append-only: this script never rewrites an existing line.
set -euo pipefail

if [ "$#" -ne 6 ]; then
    echo "usage: $0 <logfile> <phase> <decision> <why> <evidence> <result>" >&2
    exit 64
fi

logfile=$1
shift

# Collapse tabs and newlines to spaces so a cell cannot split the row, squeeze
# runs of whitespace, and trim. Then defuse the leading characters a
# spreadsheet reads as a formula.
cell() {
    local v
    v=$(printf '%s' "$1" | tr '\t\r\n' '   ' | tr -s ' ')
    v=${v# }
    v=${v% }
    case $v in
        [=+@-]*) printf "'%s" "$v" ;;
        *)       printf '%s' "$v" ;;
    esac
}

mkdir -p "$(dirname "$logfile")"

if [ ! -s "$logfile" ]; then
    printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n' > "$logfile"
fi

printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$(cell "$1")" "$(cell "$2")" "$(cell "$3")" \
    "$(cell "$4")" "$(cell "$5")" \
    >> "$logfile"
