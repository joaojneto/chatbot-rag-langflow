from elasticsearch import Elasticsearch

from langflow.custom import Component
from langflow.io import MessageTextInput, Output
from langflow.schema.message import Message


class CustomComponent(Component):
    """Elasticsearch Vector Store with advanced, customizable search capabilities."""

    display_name: str = "Elasticsearch - Search"
    description: str = "Elasticsearch Vector Store with advanced, customizable search capabilities."
    name = "Elasticsearch"
    icon = "ElasticsearchStore"

    inputs = [
        StrInput(
            name="elasticsearch_url",
            display_name="Elasticsearch URL",
            value="http://localhost:9200",
            info="URL for self-managed Elasticsearch deployments (e.g., http://localhost:9200). "
            "Do not use with Elastic Cloud deployments, use Elastic Cloud ID instead.",
        ),
        MessageTextInput(
            name="index_name",
            display_name="Index Name",
            value="langflow",
            info="The index name where the vectors will be stored in Elasticsearch cluster.",
        ),
        StrInput(
            name="api_key",
            display_name="Elastic API Key",
            value="****",
            info="API Key for Elastic Cloud authentication. If used, 'username' and 'password' are not required.",
        ),
        MessageTextInput(
            name="query_dsl",
            display_name="Query DSL",
            info="Query DSL to run on Elasticsearch",
        ),
        IntInput(
            name="number_of_results",
            display_name="Number of Results",
            info="Number of results to return.",
            value=3,
        ),
    ]
    
    outputs = [
        Output(display_name="Message", name="mapping", method="get_index_mapping"),
    ]

    def get_index_mapping(self) -> Message:
        """Fetches the index mapping from Elasticsearch."""
        headers = {"Authorization": f"ApiKey {self.api_key}"} if self.api_key else {}
        
        es = Elasticsearch(self.elasticsearch_url, headers=headers)
        
        try:
            if es.indices.exists(index=self.index_name):
                response = es.search(index=self.index_name, body=self.query_dsl)
                return response
            else:
                return "huheuheuheuheuhe"
        except Exception as e:
            return str(e)
