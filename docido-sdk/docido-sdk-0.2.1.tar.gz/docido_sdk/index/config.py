
from docido_sdk.core import (
    Component,
    ExtensionPoint,
    implements,
)
import docido_sdk.config as docido_config
from . api import (
    IndexAPIProvider,
    IndexPipelineConfig,
    PullCrawlerIndexingConfig,
)


class YamlPullCrawlersIndexingConfig(Component):
    implements(PullCrawlerIndexingConfig, IndexPipelineConfig)
    index_api_providers = ExtensionPoint(IndexAPIProvider)

    def service(self, service):
        prs = docido_config.get('pull_crawlers') or {}
        crawlers_config = prs.get('crawlers') or {}
        return (crawlers_config.get(service) or {}).get('indexing', {})

    def core(self):
        return docido_config.pull_crawlers.indexing

    def get_pipeline(self, service):
        service_config = self.service(service)
        if 'pipeline' in service_config:
            processor_pipeline = service_config.pipeline
        else:
            indexing_config = self.core()
            processor_pipeline = indexing_config.pipeline
        providers = dict([
            (p.__class__.__name__, p)
            for p in list(self.index_api_providers)
        ])
        return list(map(lambda p: providers[p], processor_pipeline))
