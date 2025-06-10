from abc import ABC, abstractmethod

class CRUDRepositoryInterface(ABC):

    @abstractmethod
    def url_request(self, url):
        pass

    @abstractmethod
    def url_posts(self, url, data):
        pass

    @abstractmethod
    def url_patch(self, url, data):
        pass

    @abstractmethod
    def url_delete(self, url):
        pass

