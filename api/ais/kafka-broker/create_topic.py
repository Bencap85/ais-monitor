from confluent_kafka.admin import AdminClient, NewTopic
from kafka_server.config import SERVER_CONFIG

admin = AdminClient(SERVER_CONFIG)
topic = NewTopic("ais_message", num_partitions=1, replication_factor=1)

fs = admin.create_topics([topic])

for topic, f in fs.items():
    try:
        f.result()  # Wait for topic creation
        print(f"Topic '{topic}' created successfully.")
    except Exception as e:
        print(e)