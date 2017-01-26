#!/bin/sh
LANG=C
SED="/usr/bin/sed -i.orig"
SPATCH="spatch --very-quiet --timeout 120 --in-place"
find -L "${LOCALPATCHES}/${PKGPATH}" "${SPATCHES}" | \
    grep '\.\(sed\|cocci\)' | \
    awk -F/ '{print $0 " " $NF}' | sort -k2 | awk '{print $1}' | \
    while read sp; do
    if ! test -f "${sp}"; then
        continue
    fi
    ext=".${sp##*.}"
    spp="${WRKSRC}/$(basename ${sp}).patch"
    for i in 1 2 3 4 5 6 7 8 9 10; do
        rm -f "${spp}"
        touch "${spp}"
        find "${WRKSRC}" | grep '\.\(c\|h\)$' | while read f; do
            if ! test -f "${f}"; then
                continue
            fi
            cp -f "${f}" "${f}.orig"
            if [ "${ext}" == ".sed" ]; then
                ${SED} -f "${sp}" "${f}"
            fi
            if [ "${ext}" == ".cocci" ]; then
                ${SPATCH} --sp-file "${sp}" "${f}" >/dev/null
            fi
            diff -u "${f}.orig" "${f}" | tee -a "${spp}"
        done
        if ! test -s "${spp}"; then
            break
        fi
        sleep 60
    done
    rm -f "${spp}"
done