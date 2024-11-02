# object-backup-system-stack.ts

import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
// import * as sqs from 'aws-cdk-lib/aws-sqs';

export class ObjectBackupSystemStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // The code that defines your stack goes here

    // example resource
    // const queue = new sqs.Queue(this, 'ObjectBackupSystemQueue', {
    //   visibilityTimeout: cdk.Duration.seconds(300)
    // });
  }
}

# storage-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

export class StorageStack extends cdk.Stack {
    public readonly sourceBucket: s3.Bucket;
    public readonly destinationBucket: s3.Bucket;
    public readonly table: dynamodb.Table;

    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        // Source bucket
        this.sourceBucket = new s3.Bucket(this, 'SourceBucket', {
            versioned: true
        });

        // Destination bucket
        this.destinationBucket = new s3.Bucket(this, 'DestinationBucket', {
            versioned: true
        });

        // DynamoDB table
        this.table = new dynamodb.Table(this, 'BackupTable', {
            partitionKey: { name: 'objectName', type: dynamodb.AttributeType.STRING },
            sortKey: { name: 'timestamp', type: dynamodb.AttributeType.NUMBER }
        });

        // Export Source Bucket ARN
        new cdk.CfnOutput(this, 'SourceBucketArn', {
            value: this.sourceBucket.bucketArn,
            exportName: 'SourceBucketArn',
        });
    }
}


# replicator-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';

interface ReplicatorStackProps extends cdk.StackProps {
    destinationBucket: s3.Bucket;
    table: dynamodb.Table;
}

export class ReplicatorStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props: ReplicatorStackProps) {
        super(scope, id, props);

        const sourceBucketArn = cdk.Fn.importValue('SourceBucketArn');

        const replicatorLambda = new lambda.Function(this, 'ReplicatorLambda', {
            runtime: lambda.Runtime.NODEJS_14_X,
            handler: 'replicator.handler',
            code: lambda.Code.fromAsset('lambda/replicator'),
            environment: {
                SOURCE_BUCKET_ARN: sourceBucketArn,
                DESTINATION_BUCKET_NAME: props.destinationBucket.bucketName,
                TABLE_NAME: props.table.tableName,
            },
        });

        props.destinationBucket.grantWrite(replicatorLambda);
        props.table.grantReadWriteData(replicatorLambda);

        // Add permissions for Replicator Lambda to read from the source bucket
        replicatorLambda.addToRolePolicy(
            new cdk.aws_iam.PolicyStatement({
                actions: ['s3:GetObject', 's3:ListBucket'],
                resources: [sourceBucketArn],
            })
        );
    }
}

# cleaner-stack.ts
import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as s3 from 'aws-cdk-lib/aws-s3';


interface CleanerStackProps extends cdk.StackProps {
    table: dynamodb.Table;
    destinationBucket: s3.Bucket;
}

export class CleanerStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props: CleanerStackProps) {
        super(scope, id, props);

        const cleanerLambda = new lambda.Function(this, 'CleanerLambda', {
            runtime: lambda.Runtime.NODEJS_14_X,
            handler: 'cleaner.handler',
            code: lambda.Code.fromAsset('lambda/cleaner')
        });

        // Grant permissions to Lambda
        props.table.grantReadWriteData(cleanerLambda);
        props.destinationBucket.grantDelete(cleanerLambda);

        // Define an EventBridge rule to trigger Lambda every 5 seconds
        const rule = new events.Rule(this, 'CleanerSchedule', {
            schedule: events.Schedule.rate(cdk.Duration.minutes(1))
        });
        rule.addTarget(new targets.LambdaFunction(cleanerLambda));
    }
}

# object-backup-system.ts
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as s3n from 'aws-cdk-lib/aws-s3-notifications';

interface ReplicatorStackProps extends cdk.StackProps {
    destinationBucket: s3.Bucket;
    table: dynamodb.Table;
}

export class ReplicatorStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props: ReplicatorStackProps) {
        super(scope, id, props);

        const sourceBucketArn = cdk.Fn.importValue('SourceBucketArn');

        const replicatorLambda = new lambda.Function(this, 'ReplicatorLambda', {
            runtime: lambda.Runtime.NODEJS_14_X,
            handler: 'replicator.handler',
            code: lambda.Code.fromAsset('lambda/replicator'),
            environment: {
                SOURCE_BUCKET_ARN: sourceBucketArn,
                DESTINATION_BUCKET_NAME: props.destinationBucket.bucketName,
                TABLE_NAME: props.table.tableName,
            },
        });

        props.destinationBucket.grantWrite(replicatorLambda);
        props.table.grantReadWriteData(replicatorLambda);

        // Add permissions for Replicator Lambda to read from the source bucket
        replicatorLambda.addToRolePolicy(
            new cdk.aws_iam.PolicyStatement({
                actions: ['s3:GetObject', 's3:ListBucket'],
                resources: [sourceBucketArn],
            })
        );
    }
}



