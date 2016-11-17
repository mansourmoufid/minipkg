#!/bin/sh
SPATCH_ARGS="--very-quiet --in-place --timeout 120"
FILES="$(find ${WRKSRC} -type f -name '*.[ch]')"
for sp in ${LOCALPATCHES}/${PKGPATH}/*.cocci ${SPATCHES}/*.cocci; do
    if ! test -f "${sp}"; then
        continue
    fi
    spp="${WRKSRC}/$(basename ${sp}).patch"
    for i in 1 2 3 4 5 6 7 8 9 10; do
        rm -f "${spp}"
        touch "${spp}"
        for f in ${FILES}; do
            if ! test -f "${f}"; then
                continue
            fi
            spatch ${SPATCH_ARGS} --sp-file "${sp}" "${f}" | tee -a "${spp}"
        done
        if ! test -s "${spp}"; then
            break
        fi
        sleep 60
    done
    rm -f "${spp}"
done
