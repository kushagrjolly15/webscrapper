from azure.cosmos import exceptions, CosmosClient, PartitionKey
import items

# Initialize the Cosmos client
endpoint = "https://intelligentwebdbcoresql.documents.azure.com:443/"
key = 'lZR5rfWRnD0jgYo6gOId9qY5oGWPLj6VbXjPifSgasd5PkNlb9fRhv1vih9sWkywjJG16DBdBxQQhdNDTzxTgA=='

# <create_cosmos_client>
client = CosmosClient(endpoint, key)
# </create_cosmos_client>

# Create a database
# <create_database_if_not_exists>
database_name = 'products'
database = client.create_database_if_not_exists(id=database_name)
# </create_database_if_not_exists>

# Create a container
# Using a good partition key improves the performance of database operations.
# <create_container_if_not_exists>
container_name = 'Products'
container = database.create_container_if_not_exists(
    id=container_name,
    partition_key=PartitionKey(path="/productid"),
    offer_throughput=400
)
# </create_container_if_not_exists>


# Add items to the container
products_to_create = [items.get_lululemon_pant(), items.get_lululemon_shirt()]

# <create_item>
for item in products_to_create:
    container.create_item(body=item)
# </create_item>

# Query these items using the SQL query syntax. Specifying the partition key value in the query allows Cosmos DB to
# retrieve data only from the relevant partitions, which improves performance <query_items>
query = "SELECT * FROM c WHERE c.productid IN ('Lululemon_pant1', 'Lululemon_shirt1')"

items = list(container.query_items(
    query=query,
    enable_cross_partition_query=True
))

request_charge = container.client_connection.last_response_headers['x-ms-request-charge']

print('Query returned {0} items. Operation consumed {1} request units'.format(len(items), request_charge))
# </query_items>
