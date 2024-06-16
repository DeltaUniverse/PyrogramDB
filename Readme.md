**PyrogramDB**

**Table of Contents**

* [Features](#features)
* [Installation](#installation)
* [Setup](#setup)
    * [Example](#example)
        * [Breakdown of Operations](#breakdown-of-operations)
* [Methods](#methods)
* [Security Considerations](#security-considerations)
* [Contributing](#contributing)
* [License](#license)

**Features**

- **Simple and Efficient:** PyrogramDB offers a straightforward approach to data storage and management for your Pyrogram-based Telegram bots.
- **CRUD Operations:** Perform essential database operations like creating (Insert), retrieving (Query), updating (Update), and deleting (Delete) records using intuitive methods.
- **Telegram Group Integration:** Leverage a dedicated Telegram group for data storage, providing a readily accessible and familiar interface for managing your bot's data.

**Installation**

Before diving in, ensure you have the following dependencies installed:

```bash
pip install pyrogram tgcrypto
```

**Setup**

1. **Create a Python Script:** Begin by creating a Python script to interact with PyrogramDB.

2. **Import Necessary Libraries:** Import the `Client` class from `pyrogram` and `PyrogramDB` from your `pyrogramdb.py` file (assuming that's where your class resides).

3. **Configure Logging:** Set up logging (optional but recommended) to track database interactions and potential errors. Use `logging.basicConfig(level=logging.INFO)` to enable informative logs.

4. **Replace Placeholders:** Update the following placeholders with your actual values:

   - `API_ID`: Your Telegram API ID
   - `API_HASH`: Your Telegram API hash
   - `BOT_TOKEN`: Your Telegram bot token
   - `CHAT_ID`: The chat ID of the Telegram group you'll use for data storage (replace the negative placeholder with the actual ID)

5. **Instantiate Pyrogram Client and PyrogramDB:** Create instances of `Client` and `PyrogramDB`:

   ```python
   app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
   db = PyrogramDB(app, CHAT_ID)
   ```

**Example**

This example demonstrates how to use PyrogramDB for basic CRUD operations:

```python
async def main():
    await app.start()

    # Sample data for insertion
    data_to_insert = {
        "name": "John Doe",
        "age": 30,
        "occupation": "Software Developer"
    }

    # Insert data
    inserted_data = await db.insert_one(data_to_insert)
    print("Inserted Data (message ID):", inserted_data)  # Returns the message ID for reference

    # Query for specific data
    query = {"name": "John Doe"}
    result = await db.get_one(query)
    print("Queried Data:", result)  # Returns the matching data dictionary

    # Update existing data (modify the value you want to change)
    new_data = {"age": 31}
    updated_data = await db.update_one(query, new_data)
    print("Updated Data:", updated_data)  # Returns the updated data dictionary

    # Delete data
    delete_success = await db.delete_one(query)
    print("Delete Successful:", delete_success)  # Returns True if deletion was successful

    await app.stop()

import asyncio
asyncio.run(main())
```

**Breakdown of Operations**

- **`insert_one(data)`:** Adds a single record to the Telegram group database. Returns the message ID of the inserted data for potential reference.
- **`get_one(query)`:** Retrieves the first record that matches the provided query dictionary. Returns the matching data dictionary or `None` if no match is found.
- **`update_one(query, new_data)`:** Modifies the first record that satisfies the query with the new data provided. Returns the updated data dictionary or `None` if no match is found.
- **`delete_one(query)`:** Deletes the first record that matches the query. Returns `True` if deletion was successful, `False` otherwise.

**Security Considerations**

While PyrogramDB offers convenience, it's essential to be mindful of security implications when storing data in a Telegram group, especially for sensitive information. Consider the following precautions:

- **Data Encryption:** Encrypt sensitive data before storing it in the Telegram group.
- **Access Control:** Limit access to the Telegram group to only trusted users or administrators.
- **Logging and Monitoring:** Implement robust logging and monitoring to detect any unauthorized access or anomalies in data transactions.
- **Bot Permissions:** Restrict bot permissions to only those necessary for its operations to minimize potential attack vectors.
