import boto3

# connect to DynamoDB
dynamodb = boto3.resource("dynamodb", region_name="us-east-2")

table = dynamodb.Table("products")

# test read
response = table.scan(Limit=1)

print("Connection successful")
print(response)