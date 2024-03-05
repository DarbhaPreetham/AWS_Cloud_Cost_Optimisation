import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')

    # Get all the EBS Snapshots
    response = ec2.describe_snapshots(OwnerIds=['self'])

    # Get all active EC2 instance IDs

    instance_response = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    active_instance_ids = set()

    for reservation in instance_response['Reservations']:
        for instance in reservation['Instances']:
            active_instance_ids.add(instance['InstanceId'])

        # Iterate through each snapshot and delete if it's not attached to any volume or the volume is not attched to a running instance
            
        for snapshot in response['Snapshots']:
            snapshot_id = snapshot['SnapshotID']
            volume_id = snapshot.get('VolumeId')

            if not volume_id:
                # Delete the snapshot if it's not attached to any volume
                ec2.delete_snapshot(SnapshotId=snapshot_id)
                print(f"Deleted EBS snapshot {snapshot_id} as it was not attached to any volume.")
            else:
                # Check if the volume still exists
                try:
                    volume_response = ec2.describe_volumes(VolumeIds=[volume_id])
                    if not volume_response['Volumes'] [0] ['Attachments']:
                        ec2.delete_snapshot(SnapshotId=snapshot_id)
                        print(f"Deleted EBS snapshot {snapshot_id} as it was taken from a volume not attached to any running instance.")
                except ec2.exceptions.ClientError as e:
                    if e.responce['Error']['Code'] == 'InvalidVolume.NotFound':
                        # The Volume associated with the snapshot is not found 
                        ec2.delete_snapshot(SnapshotId=snapshot_id)
                        print(f"Deleted EBS snapshot {snapshot_id} as its associated volume was not found.")
