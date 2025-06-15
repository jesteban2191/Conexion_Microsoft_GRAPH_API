from abc import ABC, abstractmethod
from typing import List, Dict, Any

class HandlerSharepointStrategyInterface(ABC):

    @abstractmethod
    def get_collections(self, auth):
        pass

    @abstractmethod
    def get_fields(self, collection_name = "", collection_id = ""):
        pass
    
    @abstractmethod
    def get_items(self, colection_name="", collection_id=""):
        pass

    @abstractmethod
    def create_item (self, data, collection_name="", collection_id=""):
        pass

    @abstractmethod
    def delete_items (self, collection_name="", collection_id ="", id_items=[], delete_all = False):
        pass

    @abstractmethod
    def update_collection(self, data, pk, collection_name="", collection_id="", delete = True, insert = True, delete_duplicates = False):
        pass

