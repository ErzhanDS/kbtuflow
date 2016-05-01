import boto3
import base64

"""
NOTE

    The new way to store secrets in sauron is to use secrets.get_secret(key)

    The way this works is we store the encrypted blob in a DynamoDB table, and
    then decrypt using KMS.  You no longer need to:
       * store the encrypted blob in the codebase
       * map the right encrypted blob to the deployment stage

    You can continue to use @cached_property methods for convenience, but these
    should eventually be moved to use get_secret()

    You can store secrets using the CLI defined here, e.g.:

        python -m sauron.auth --mode encrypt --key jlf-is-cool --value bao-is-lame
"""


class SecretsClass(object):

    @property
    def secrets_table(self):
        ddb = boto3.resource('dynamodb')
        return ddb.Table('secrets')

    @property
    def iam(self):
        return boto3.client('iam')

    @property
    def kms(self):
        return boto3.client('kms')

    def get_kms_key_id(self):
        return 'd337bcfa-e786-46f9-af50-88f7d2960dc4'

    def get_secret(self, key):
        try:
            response = self.secrets_table.get_item(Key={'secret_key': key})
            blob = base64.b64decode(response['Item']['value'])
            response = self.kms.decrypt(CiphertextBlob=blob)
            return response['Plaintext']
        except Exception as e:
            raise e

    def set_secret(self, key, value, overwrite=False):
        if not (key and value):
            raise Exception('key and value cannot be None')

        try:
            response = self.kms.encrypt(KeyId=self.get_kms_key_id(), Plaintext=value)
            b64 = base64.b64encode(response['CiphertextBlob'])

            kwargs = {
                'Item': {
                    'secret_key': key,
                    'value': b64
                },
            }
            if not overwrite:
                kwargs['ConditionExpression'] = 'attribute_not_exists(secret_key)'

            self.secrets_table.put_item(**kwargs)

        except Exception as e:
            raise e

secrets = SecretsClass()
