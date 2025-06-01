import os
import re
from typing import Dict, List, Union
from dataclasses import asdict
import json

from lily.utils.config import load_config
from lily.utils.log import logger
from lily.data.models import ChatMLMessages, ChatMLMessage, RawMessage, QaPair

class DataProcessor:
    def __init__(self):
        self.config = load_config(arg_type="make_dataset")
        self.raw_folder = "./dataset/raw"
        self.qa_pair_output_path = "./dataset/res/sft/sft-my.json"
        self.chatml_output_path = "./dataset/res/sft/sft-my.jsonl"
        self.system_prompt = self.config.get("default_system")


    def process(self):
        raw_files = self._list_raw_files()
        if not raw_files:
            logger.error(f"Error：folder '{self.raw_folder}' is empty.")
            return

        all_qa_pair_list: List[QaPair] = []
        start_qa_pair_id = 1 
        for raw_file in raw_files:
            raw_messages_list = self._load_raw_file(raw_file)
            start_qa_pair_id, qa_pair_list = self._raw_message_list_to_qa_pair_list(start_qa_pair_id, raw_messages_list)
            all_qa_pair_list.extend(qa_pair_list)
        self._save_qa_pair_list(all_qa_pair_list)
        all_chatml_messages = self._qa_pair_list_to_chatml_messages_list(all_qa_pair_list)
        self._save_chatml_messages_list(all_chatml_messages)


    def _list_raw_files(self):
        if not os.path.exists(self.raw_folder) or not os.listdir(self.raw_folder):
            logger.error(f"Error：folder '{self.raw_folder}' does not exist or is empty.")
            return
        raw_files = []
        for txt_filename in os.listdir(self.raw_folder):
            txt_filepath = os.path.join(self.raw_folder, txt_filename)
            raw_files.append(txt_filepath)
        raw_files.sort()
        return raw_files


    def _load_raw_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [self._raw_line_to_raw_message(line) for line in lines]


    def _raw_message_list_to_qa_pair_list(self, start_qa_pair_id, raw_message_list):
        qa_pair_list: List[QaPair] = []
        qa_pair_id = start_qa_pair_id
        last_user_content = ""
        last_assistant_content = ""
        last_user = ""
        for i, raw_message in enumerate(raw_message_list):
            # merge consecutive messages into a single message.
            if last_user == raw_message.user:
                if raw_message.is_aside():
                    continue
                elif raw_message.is_assistant():
                    if last_assistant_content == "":
                        last_assistant_content = raw_message.content
                    else:
                        last_assistant_content += " " + raw_message.content
                else:
                    if last_user_content == "":
                        last_user_content = raw_message.content
                    else:
                        last_user_content += " " + raw_message.content
                continue

            # add question and answer pair to sft_messages_list
            if last_user_content != "" and last_assistant_content != "":
                qa_pair_list.append(self._create_qa_pair(qa_pair_id, last_user_content, last_assistant_content))
                qa_pair_id += 1
                last_user_content = ""
                last_assistant_content = ""

            last_user = raw_message.user
            if raw_message.is_aside():
                continue
            elif raw_message.is_assistant():
                last_assistant_content = raw_message.content
            else:
                last_user_content = raw_message.content
            
        if last_user_content != "" and last_assistant_content != "":
            qa_pair_list.append(self._create_qa_pair(qa_pair_id, last_user_content, last_assistant_content))
            qa_pair_id += 1
        return qa_pair_id, qa_pair_list


    def _raw_line_to_raw_message(self, line):
        if line.startswith("Lily:"):
            return RawMessage(user="Lily", content=line[6:].strip())
        match = re.match(r'^(\w+): (.+)', line)
        if match:
            name, content = match.groups()
            return RawMessage(user=name, content=content)
        else:
            return RawMessage(user="__ASIDE__", content=line.strip())


    def _create_qa_pair(self, qa_pair_id: int, user_content: str, assistant_content: str) -> QaPair:
        return QaPair(id=qa_pair_id, 
                      system=self.system_prompt, 
                      instruction=user_content, 
                      output=assistant_content, 
                      history=[], 
                      time=None, 
                      score=0)

  
    def _qa_pair_to_chatml_messages(self, qa_pair: QaPair) -> ChatMLMessages:
        sft_message_list: List[ChatMLMessage] = []
        sft_message_list.append(ChatMLMessage(role="system", content=qa_pair.system))
        sft_message_list.append(ChatMLMessage(role="user", content=qa_pair.instruction))
        sft_message_list.append(ChatMLMessage(role="assistant", content=qa_pair.output))
        return ChatMLMessages(messages=sft_message_list)
    

    def _qa_pair_list_to_chatml_messages_list(self, qa_pair_list: List[QaPair]) -> List[ChatMLMessages]:
        chatml_messages_list: List[ChatMLMessages] = []
        for qa_pair in qa_pair_list:
            chatml_messages = self._qa_pair_to_chatml_messages(qa_pair)
            chatml_messages_list.append(chatml_messages)
        return chatml_messages_list
    

    def _save_qa_pair_list(self, qa_pair_list: List[QaPair]):
        os.makedirs(os.path.dirname(self.qa_pair_output_path), exist_ok=True)
        with open(self.qa_pair_output_path, "w", encoding="utf-8") as f:
            qa_pair_dicts = [asdict(qa_pair) for qa_pair in qa_pair_list]
            json.dump(qa_pair_dicts, f, ensure_ascii=False, indent=2)
        logger.success(f"saved qa pairs for sft. count={len(qa_pair_list)}, path={self.qa_pair_output_path}")


    def _save_chatml_messages_list(self, chatml_messages_list: List[ChatMLMessages]):
        os.makedirs(os.path.dirname(self.chatml_output_path), exist_ok=True)
        with open(self.chatml_output_path, "w", encoding="utf-8") as f:
            for chatml_messages in chatml_messages_list:
                json.dump(asdict(chatml_messages), f, ensure_ascii=False)
                f.write("\n")
        logger.success(f"saved chatml messages for sft. count={len(chatml_messages_list)}, path={self.chatml_output_path}")