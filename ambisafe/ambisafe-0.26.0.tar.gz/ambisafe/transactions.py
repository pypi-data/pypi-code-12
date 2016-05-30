import json
import logging
from ambisafe.containers import Container

logger = logging.getLogger('ambisafe')


class BaseTransaction(object):
    def __init__(self, hex, fee, sighashes):
        self.hex = hex
        self.fee = fee
        self.sighashes = sighashes

    def to_json(self):
        raise NotImplemented


class UserSideTransaction(BaseTransaction):
    def __init__(self, hex, fee, sighashes, user_signatures=None):
        super(UserSideTransaction, self).__init__(hex, fee, sighashes)
        self.user_signatures = user_signatures or []

    def to_dict(self):
        return {
            'hex': self.hex,
            'fee': self.fee,
            'sighashes': self.sighashes,
            'user_signatures': self.user_signatures,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class SimpleTransaction(BaseTransaction):
    def to_json(self):
        return {
            'hex': self.hex,
            'fee': self.fee,
            'sighashes': self.sighashes,
        }


class Wallet4Transaction(BaseTransaction):
    def __init__(self, hex, fee, sighashes, operator_signatures=None, user_signatures=None):
        super(Wallet4Transaction, self).__init__(hex, fee, sighashes)
        self.user_signatures = user_signatures or []
        self.operator_signatures = operator_signatures or []

    def to_dict(self):
        return {
            'hex': self.hex,
            'fee': self.fee,
            'sighashes': self.sighashes,
            'user_signatures': self.user_signatures,
            'operator_signatures': self.operator_signatures,
        }

    def to_json(self):
        return json.dumps(self.to_dict())


class RecoveryTransaction(Wallet4Transaction):
    def __init__(self, operator, recovery_transaction, account_id=None, recovery_address=None, entropy=None,
                 public_key=None, operator_backup_signatures=None, operator_signatures=None):
        self.account_id = account_id
        self.recovery_address = recovery_address
        self.entropy = entropy
        self.public_key = public_key
        self.operator_backup_signatures = operator_backup_signatures
        self.operator_container = Container(**operator)
        super(RecoveryTransaction, self).__init__(recovery_transaction['hex'],
                                                  recovery_transaction['fee'],
                                                  recovery_transaction['sighashes'],
                                                  operator_signatures=operator_signatures)

    def to_dict(self):
        if self.account_id:
            return {
                'operator': self.operator_container.__dict__,
                'recovery_transaction': {
                    'hex': self.hex,
                    'fee': self.fee,
                    'sighashes': self.sighashes,
                },
                'account_id': self.account_id,
                'operator_signatures': self.operator_signatures,
                'operator_backup_signatures': self.user_signatures,
                'recovery_address': self.recovery_address,
            }
        else:
            return {
                'operator': self.operator_container.__dict__,
                'recovery_transaction': {
                    'hex': self.hex,
                    'fee': self.fee,
                    'sighashes': self.sighashes,
                },
                'entropy': self.entropy,
                'public_key': self.public_key,
                'operator_signatures': self.operator_signatures,
                'operator_backup_signatures': self.operator_backup_signatures,
                'recovery_address': self.recovery_address,
            }

    def to_json(self):
        logger.debug('Recovery transactions COMPLETED SUBMIT JSON: {}'
                     .format(json.dumps(self.to_dict())))
        return json.dumps(self.to_dict())


class GrantTransaction(BaseTransaction):
    def __init__(self, hex, fee, sighashes, signatures=None):
        super(GrantTransaction, self).__init__(hex, fee, sighashes)
        self.signatures = signatures or []

    def add_signature(self, signature_number, sigs):
        if any(signature for signature in self.signatures if signature['key'] == str(signature_number)):
            raise ValueError('Sigs for {} signature_number already exists'.format(signature_number))

        self.signatures.append({
            'key': signature_number,
            'sigs': sigs,
        })

    def to_dict(self):
        return {
            'hex': self.hex,
            'fee': self.fee,
            'sighashes': self.sighashes,
            'signatures': self.signatures,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
