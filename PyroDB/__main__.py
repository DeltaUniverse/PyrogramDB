"""
(c) Jigarvarma2005
(c) Troublescope

Simple database for pyrogram based bots.

Feel free to contribute.
"""

import asyncio
import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Union

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.errors import FloodWait


class PyrogramDB:
    """Simple Database for Pyrogram based bots"""

    def __init__(self, client: Client, chat_id: int):
        """Initialize the database

        bot: pyrogram client instance
        chat_id: ID of a group with admin privileges
        """
        self.client = client
        self.chat_id = chat_id
        self.logger = logging.getLogger(__name__)

        if not isinstance(client, Client):
            raise TypeError("User must be a Pyrogram Client")
        try:
            client.start()
        except:
            pass

        chat_member_status = self.client.get_chat_member(chat_id, "me").status
        if chat_member_status not in [
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER,
        ]:
            raise Exception("User is not admin in the chat")

        chat_type = self.client.get_chat(chat_id).type
        if chat_type == ChatType.PRIVATE:
            raise Exception("Chat must be a group")

        try:
            client.stop()
        except:
            pass

    def validate(
        self, data: Union[str, List[Any], Dict[str, Any]], is_entry: bool = False
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """Validate the entered data"""

        def parse_data(
            data: Union[str, List[Any], Dict[str, Any]], is_entry: bool
        ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
            try:
                if isinstance(data, list):
                    return [self.validate(item, is_entry) for item in data]
                elif isinstance(data, str):
                    if len(data) > 4090:
                        raise ValueError("Data must be less than 4090 characters")
                    try:
                        data = json.loads(data)
                    except json.JSONDecodeError:
                        data = json.loads(json.dumps(data))
                if is_entry and "_id" not in data:
                    data["_id"] = uuid.uuid4().hex
            except Exception as e:
                raise ValueError(f"Invalid data: {e}")
            return data

        return parse_data(data, is_entry)

    def dict_to_str(self, data: Union[Dict[str, Any], str]) -> str:
        """Convert dict to str"""
        if isinstance(data, dict):
            return json.dumps(data)
        return data

    async def get_many(
        self, data: Union[str, Dict[str, Any]], limit: int = 100, is_dev: bool = False
    ) -> Optional[List[Union[Dict[str, Any], Any]]]:
        """Get many results of query

        args:
            data: query data
            limit: limit the query (defaults to 100)
            is_dev: return list of pyrogram message object instead dict

        return list of results"""
        data = self.validate(data)
        try:
            all_data = []
            async for message in self.client.search_messages(
                chat_id=self.chat_id, query=self.dict_to_str(data), limit=limit
            ):
                if not is_dev:
                    all_data.append(self.validate(message.text))
                else:
                    all_data.append(message)
            return all_data
        except Exception as e:
            self.logger.exception(f"Failed to get many: {e}")
            return None

    async def get_one(
        self, data: Union[str, Dict[str, Any]], is_dev: bool = False
    ) -> Optional[Union[Dict[str, Any], Any]]:
        """Get first result of query

        args:
            data: query data
            is_dev: return pyrogram message object instead dict

        return dict"""
        data = self.validate(data)
        try:
            async for msg in self.client.search_messages(
                chat_id=self.chat_id, query=self.dict_to_str(data), limit=1
            ):
                if msg:
                    return self.validate(msg.text) if not is_dev else msg
        except Exception as e:
            self.logger.exception(f"Failed to get one: {e}")
        return None

    async def insert_one(
        self, data: Union[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Insert one data

        args:
            data: dict of data

        returns dict"""
        data = self.validate(data, is_entry=True)
        try:
            await self.client.send_message(
                chat_id=self.chat_id, text=self.dict_to_str(data)
            )
            return data
        except Exception as e:
            self.logger.exception(f"Failed to insert one: {e}")
            return None

    async def insert_many(
        self, data: List[Union[str, Dict[str, Any]]]
    ) -> Optional[List[Dict[str, Any]]]:
        """Insert many data at once

        args:
            data: list of dict data

        returns list of dict"""
        data = self.validate(data, is_entry=True)
        insert_data = []
        try:
            for item in data:
                try:
                    await self.client.send_message(
                        chat_id=self.chat_id, text=self.dict_to_str(item)
                    )
                    insert_data.append(item)
                except FloodWait as e:
                    await asyncio.sleep(e.value)  # 'e.x' changed to 'e.value'
            return insert_data
        except Exception as e:
            self.logger.exception(f"Failed to insert many: {e}")
            return None

    async def delete_one(self, data: Union[str, Dict[str, Any]]) -> bool:
        """Delete a data

        args:
            data: key to delete

        returns bool"""
        data = self.validate(data)
        try:
            msg = await self.get_one(data, is_dev=True)
            if msg:
                await msg.delete()
                return True
        except Exception as e:
            self.logger.exception(f"Failed to delete one: {e}")
        return False

    async def delete_many(
        self, data: Union[str, Dict[str, Any]], limit: int = 100
    ) -> bool:
        """Delete many data at once

        args:
            data: list of keys

        returns bool"""
        data = self.validate(data)
        try:
            msgs = await self.get_many(data, limit=limit, is_dev=True)
            for msg in msgs:
                await msg.delete()
            return True
        except Exception as e:
            self.logger.exception(f"Failed to delete many: {e}")
            return False

    async def update_one(
        self, data: Union[str, Dict[str, Any]], new_data: Union[str, Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Update first query result with new data

        args:
            data: key to find the data
            new_data: new data to be updated with

        returns dict"""
        try:
            msg = await self.get_one(data, is_dev=True)
            if msg:
                old_data = self.validate(msg.text)
                new_data = self.validate(new_data)
                old_data.update(new_data)
                await msg.edit_text(self.dict_to_str(old_data))
                return old_data
        except Exception as e:
            self.logger.exception(f"Failed to update one: {e}")
        return None

    async def update_many(
        self,
        data: Union[str, Dict[str, Any]],
        new_data: Union[str, Dict[str, Any]],
        limit: int = 100,
    ) -> Optional[List[Dict[str, Any]]]:
        """Update all query results with new data

        args:
            data: key to find the data
            new_data: new data to be updated with

        returns list of dict"""
        updated_data = []
        try:
            data = self.validate(data)
            msgs = await self.get_many(data, limit=limit, is_dev=True)
            for msg in msgs:
                old_data = self.validate(msg.text)
                old_data.update(self.validate(new_data))
                await msg.edit_text(self.dict_to_str(old_data))
                updated_data.append(old_data)
            return updated_data
        except Exception as e:
            self.logger.exception(f"Failed to update many: {e}")
            return None
