from aws_cdk import (
    Stack,
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_events as events,
    aws_events_targets as targets,
    Duration
)
from constructs import Construct


class CleanerStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, destination_bucket: s3.Bucket, table: dynamodb.Table,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Define the Cleaner Lambda function
        cleaner_lambda = lambda_.Function(
            self, 'CleanerLambda',
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler='cleaner_handler.handler',
            code=lambda_.Code.from_asset('lambda'),
            timeout=Duration.seconds(300),
            environment={
                'TABLE_NAME': table.table_name,
                'DESTINATION_BUCKET_NAME': destination_bucket.bucket_name,
            }
        )

        # Set up a rule to trigger Cleaner Lambda every minute
        events.Rule(self, 'CleanerSchedule',
                    schedule=events.Schedule.rate(Duration.minutes(1)),
                    targets=[targets.LambdaFunction(cleaner_lambda)]
                    )

        # Grant delete permissions to the destination bucket and read/write permissions to the table
        destination_bucket.grant_delete(cleaner_lambda)
        table.grant_read_write_data(cleaner_lambda)
