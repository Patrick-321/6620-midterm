from aws_cdk import Stack, Fn, CfnOutput
from constructs import Construct


class ReplicatorStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        source_bucket_arn = Fn.import_value('SourceBucketArn')
        replicator_lambda_arn = Fn.import_value('ReplicatorLambdaArn')
        CfnOutput(self, 'ReplicatorLambdaImportedArn', value=replicator_lambda_arn,
                  export_name='ReplicatorLambdaImportedArn')