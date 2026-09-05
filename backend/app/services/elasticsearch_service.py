from elasticsearch import Elasticsearch
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self, url: str):
        self.client = Elasticsearch([url])
        self.index_name = "jobs"
    
    def create_index(self):
        """Create Elasticsearch index with mappings"""
        mapping = {
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"},
                            "completion": {"type": "completion"}
                        }
                    },
                    "company_name": {
                        "type": "text",
                        "fields": {
                            "keyword": {"type": "keyword"}
                        }
                    },
                    "description": {"type": "text"},
                    "skills": {"type": "keyword"},
                    "category": {"type": "keyword"},
                    "location": {"type": "text"},
                    "remote_type": {"type": "keyword"},
                    "salary_min": {"type": "float"},
                    "salary_max": {"type": "float"},
                    "posted_at": {"type": "date"},
                    "is_active": {"type": "boolean"},
                    "source_url": {"type": "keyword", "index": False},
                    "apply_url": {"type": "keyword", "index": False},
                    "source_name": {"type": "keyword"}
                }
            },
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "job_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop", "snowball"]
                        }
                    }
                }
            }
        }
        
        if not self.client.indices.exists(index=self.index_name):
            self.client.indices.create(index=self.index_name, body=mapping)
    
    def index_job(self, job: Dict[str, Any]):
        """Index a single job"""
        self.client.index(
            index=self.index_name,
            id=job.get("id"),
            document=job
        )
    
    def search_jobs(
        self,
        query: str,
        filters: Dict = None,
        page: int = 1,
        size: int = 20
    ) -> Dict:
        """Search jobs with filters"""
        must_conditions = []
        
        if query:
            must_conditions.append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "description", "company_name^2", "skills^2"],
                    "type": "best_fields",
                    "fuzziness": "AUTO"
                }
            })
        
        if filters:
            for key, value in filters.items():
                if value:
                    must_conditions.append({
                        "term": {key: value}
                    })
        
        body = {
            "from": (page - 1) * size,
            "size": size,
            "query": {
                "bool": {
                    "must": must_conditions if must_conditions else [{"match_all": {}}]
                }
            },
            "sort": [
                {"posted_at": {"order": "desc"}},
                {"_score": {"order": "desc"}}
            ],
            "highlight": {
                "fields": {
                    "title": {},
                    "description": {"fragment_size": 150}
                }
            }
        }
        
        response = self.client.search(
            index=self.index_name,
            body=body
        )
        
        return {
            "total": response["hits"]["total"]["value"],
            "jobs": [hit["_source"] for hit in response["hits"]["hits"]],
            "took": response["took"]
        }
    
    def suggest(self, prefix: str, field: str = "title") -> List[str]:
        """Get autocomplete suggestions"""
        body = {
            "suggest": {
                "job-suggestions": {
                    "prefix": prefix,
                    "completion": {
                        "field": f"{field}.completion",
                        "size": 10
                    }
                }
            }
        }
        
        response = self.client.search(
            index=self.index_name,
            body=body
        )
        
        suggestions = []
        for suggestion in response["suggest"]["job-suggestions"]:
            for option in suggestion["options"]:
                suggestions.append(option["text"])
        
        return suggestions