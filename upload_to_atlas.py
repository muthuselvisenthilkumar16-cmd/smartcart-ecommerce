from pymongo import MongoClient

# Local MongoDB
local_client = MongoClient("mongodb://localhost:27017/")
local_db = local_client["ecommerce_db"]

# MongoDB Atlas
password = "selvi160806"

atlas_uri = f"mongodb+srv://smartcart_user:{password}@cluster0.pwoc2qw.mongodb.net/?appName=Cluster0"

atlas_client = MongoClient(atlas_uri)
atlas_db = atlas_client["ecommerce_db"]

print("Connected to both databases!")

collections = local_db.list_collection_names()

print("\nCollections found:")
print(collections)

for collection_name in collections:

    local_collection = local_db[collection_name]
    atlas_collection = atlas_db[collection_name]

    data = list(local_collection.find())

    if data:

        atlas_collection.delete_many({})

        atlas_collection.insert_many(data)

        print(
            collection_name,
            "->",
            len(data),
            "documents copied"
        )

    else:
        print(collection_name, "-> empty")

print("\nData transfer completed successfully!")