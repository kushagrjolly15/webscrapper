import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants

url = 'https://intelligentwebdbcoresql.documents.azure.com:443/'
key = 'lZR5rfWRnD0jgYo6gOId9qY5oGWPLj6VbXjPifSgasd5PkNlb9fRhv1vih9sWkywjJG16DBdBxQQhdNDTzxTgA=='
client = cosmos_client.CosmosClient(url, {'masterKey':key})

database_id = 'products'
container_id = 'SizeGuideInformation'
database = client.get_database_client(database_id)
container = database.get_container_client(container_id)

# Accepts a product in JSON format and creates an item in the Products container.
def create_product(product):
    print('Creating Product with ID :' + product['id'])
    container.create_item(body=product)

def get_all_items():
    item_list = list(container.read_all_items())
    print('Found {0} items'.format(item_list.__len__()))
    return item_list

def get_item_by_id(id):
    return container.read_item(item=id, partition_key=id)

def read_products(product_field_name, product_field_value):
    query_results = list(container.query_items(
        query="SELECT * FROM r WHERE r."+product_field_name+"=@id",
        parameters=[
            {"name":"@id", "value":product_field_value}
        ],
        enable_cross_partition_query=True
    ))

    print('Total number of Items returned: {0}'.format(len(query_results)))
    return query_results

def delete_product(id):
    container.delete_item(item=id, partition_key=id)
    print('Product with id {0} deleted successfully'.format(id))

def update_product(id, product_field_name, product_field_value):
    try:
        product = container.read_item(item=id, partition_key=id)
        product[product_field_name] = product_field_value
        container.replace_item(item=product, body=product)
        print('Product Updated Successfully')
    except:
        print('Product not found in the database.')

