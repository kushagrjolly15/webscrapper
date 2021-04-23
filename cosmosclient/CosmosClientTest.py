import CosmosClient as cc
import items

def run_sample():
    product = items.get_shopify_product()

    print("1. Create a product in DB:\n")
    cc.create_product(product)
    print("\n\n")

    print("2. Retrive product using id:\n")
    print(cc.get_item_by_id('Test_4572064120921'))
    print("\n\n")

    print("3. Update product value:\n")
    cc.update_product('Test_4572064120921','colors','Dirty Color')
    print(cc.get_item_by_id('Test_4572064120921'))
    print("\n\n")


    print("4. Query Products using property value:\n")
    print(cc.read_products('colors','Dirty Color'))
    print("\n\n")

    
    # print("5. Delete product:\n")
    # cc.delete_product('Test_4572064120921')
    # try:
    #     print(cc.get_item_by_id('Test_4572064120921'))
    # except:
    #     print('Product is not found in the Database')


if __name__ == '__main__':
    run_sample()
