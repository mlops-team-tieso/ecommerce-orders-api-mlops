import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-2")
table = dynamodb.Table("orders")

def test_dynamo_connection():
    response = table.scan(Limit=1)
    assert response is not None