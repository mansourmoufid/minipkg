#!/bin/sh
LANG=C
SED="/usr/bin/sed -i.orig"
SPATCH="spatch --very-quiet --timeout 120 --in-place"
for sp in ${LOCALPATCHES}/${PKGPATH}/*.sed ${SPATCHES}/*.sed \
    ${LOCALPATCHES}/${PKGPATH}/*.cocci ${SPATCHES}/*.cocci; do
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
