import os
import re
from typing import Dict, List, Union

from lily.utils.config import load_config
from lily.utils.log import logger
from lily.data.models import SftMessages, SftMessage, RawMessage

class DataProcessor:
    def __init__(self):
        self.config = load_config("make_dataset")
        self.raw_folder = "./dataset/raw"
        self.system_prompt = self.config.get("default_system")

    def process(self):
        raw_files = self.get_raw_files()
        if not raw_files:
            logger.error(f"Error：folder '{self.raw_folder}' is empty.")
            return

        all_sft_messages_list: List[SftMessages] = [] 
        for raw_file in raw_files:
            raw_messages_list = self.load_raw_file(raw_file)
            all_sft_messages_list.extend(self.raw_messages_to_sft_messages_list(raw_messages_list))
        self.save_sft_messages(all_sft_messages_list)

    def get_raw_files(self):
        if not os.path.exists(self.raw_folder) or not os.listdir(self.raw_folder):
            logger.error(f"Error：folder '{self.raw_folder}' does not exist or is empty.")
            return
        raw_files = []
        for txt_filename in os.listdir(self.raw_folder):
            txt_filepath = os.path.join(self.raw_folder, txt_filename)
            raw_files.append(txt_filepath)
        raw_files.sort()
        return raw_files
    
    def load_raw_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [self.raw_line_to_message(line) for line in lines]


    def raw_messages_to_sft_messages_list(self, raw_message_list):
        sft_messages_list: List[SftMessages] = []
        user_content = ""
        assistant_content = ""
        last_user = ""
        for i, raw_message in enumerate(raw_message_list):
            # 用户连续发言合并成一条
            if last_user == raw_message.user:
                if raw_message.is_aside():
                    continue
                elif raw_message.is_assistant():
                    if assistant_content == "":
                        assistant_content = raw_message.content
                    else:
                        assistant_content += " " + raw_message.content
                else:
                    if user_content == "":
                        user_content = raw_message.content
                    else:
                        user_content += " " + raw_message.content
                continue

            # 完整的对话加入列表
            if user_content != "" and assistant_content != "":
                sft_messages_list.append(self.create_sft_messages(user_content, assistant_content))
                user_content = ""
                assistant_content = ""

            user = raw_message.user
            if raw_message.is_aside():
                continue
            elif raw_message.is_assistant():
                assistant_content = raw_message.content
            else:
                user_content = raw_message.content
            
        # 完整的对话加入列表
        if user_content != "" and assistant_content != "":
            sft_messages_list.append(self.create_sft_messages(user_content, assistant_content))


    def raw_line_to_message(self, line):
        if line.startswith("Lily:"):
            return RawMessage(user="Lily", content=line[6:].strip())
        match = re.match(r'^(\w+): (.+)', line)
        if match:
            name, content = match.groups()
            return RawMessage(user=name, content=content)
        else:
            return RawMessage(user="__ASIDE__", content=line.strip())


    def create_sft_messages(self, user_content: str, assistant_content: str) -> SftMessages:
        sft_message_list = List[SftMessage] = []
        sft_message_list.append(SftMessage(role="system", content=self))
        sft_message_list.append(SftMessage(role="user", content=user_content))
        sft_message_list.append(SftMessage(role="assistant", content=assistant_content))
        return SftMessages(messages=sft_message_list)
    

    def save_sft_messages(self, sft_messages_list: List[SftMessages]):
        # todo: Implement save_sft_messages
        pass