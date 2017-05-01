// Copyright (c) 2011-2014 The Sandrocoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef SANDROCOIN_QT_SANDROCOINADDRESSVALIDATOR_H
#define SANDROCOIN_QT_SANDROCOINADDRESSVALIDATOR_H

#include <QValidator>

/** Base58 entry widget validator, checks for valid characters and
 * removes some whitespace.
 */
class SandrocoinAddressEntryValidator : public QValidator
{
    Q_OBJECT

public:
    explicit SandrocoinAddressEntryValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

/** Sandrocoin address widget validator, checks for a valid sandrocoin address.
 */
class SandrocoinAddressCheckValidator : public QValidator
{
    Q_OBJECT

public:
    explicit SandrocoinAddressCheckValidator(QObject *parent);

    State validate(QString &input, int &pos) const;
};

#endif // SANDROCOIN_QT_SANDROCOINADDRESSVALIDATOR_H
