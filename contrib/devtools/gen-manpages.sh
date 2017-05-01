#!/bin/sh

TOPDIR=${TOPDIR:-$(git rev-parse --show-toplevel)}
SRCDIR=${SRCDIR:-$TOPDIR/src}
MANDIR=${MANDIR:-$TOPDIR/doc/man}

SANDROCOIND=${SANDROCOIND:-$SRCDIR/sandrocoind}
SANDROCOINCLI=${SANDROCOINCLI:-$SRCDIR/sandrocoin-cli}
SANDROCOINTX=${SANDROCOINTX:-$SRCDIR/sandrocoin-tx}
SANDROCOINQT=${SANDROCOINQT:-$SRCDIR/qt/sandrocoin-qt}

[ ! -x $SANDROCOIND ] && echo "$SANDROCOIND not found or not executable." && exit 1

# The autodetected version git tag can screw up manpage output a little bit
BTCVER=($($SANDROCOINCLI --version | head -n1 | awk -F'[ -]' '{ print $6, $7 }'))

# Create a footer file with copyright content.
# This gets autodetected fine for sandrocoind if --version-string is not set,
# but has different outcomes for sandrocoin-qt and sandrocoin-cli.
echo "[COPYRIGHT]" > footer.h2m
$SANDROCOIND --version | sed -n '1!p' >> footer.h2m

for cmd in $SANDROCOIND $SANDROCOINCLI $SANDROCOINTX $SANDROCOINQT; do
  cmdname="${cmd##*/}"
  help2man -N --version-string=${BTCVER[0]} --include=footer.h2m -o ${MANDIR}/${cmdname}.1 ${cmd}
  sed -i "s/\\\-${BTCVER[1]}//g" ${MANDIR}/${cmdname}.1
done

rm -f footer.h2m
