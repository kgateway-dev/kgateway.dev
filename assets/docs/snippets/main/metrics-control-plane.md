Name|Type|Labels|Help
--|--|--|--
kgateway_agentgateway_xds_rejects_total|counter||Total number of xDS responses rejected by agentgateway proxy
kgateway_controller_reconcile_duration_seconds|histogram|controller, name, namespace|Reconcile duration for controller
kgateway_controller_reconciliations_running|gauge|controller, name, namespace|Number of reconciliations currently running
kgateway_controller_reconciliations_total|counter|controller, name, namespace, result|Total number of controller reconciliations
kgateway_resources_managed|gauge|namespace, parent, resource|Current number of resources managed
kgateway_resources_status_sync_duration_seconds|histogram|gateway, namespace, resource|Duration of time for a resource update to receive a status report
kgateway_resources_status_syncs_completed_total|counter|gateway, namespace, resource|Total number of status syncs completed for resources
kgateway_resources_status_syncs_started_total|counter|gateway, namespace, resource|Total number of status syncs started
kgateway_resources_updates_dropped_total|counter||Total number of resources metrics updates dropped. If this metric is ever greater than 0, all resources subsystem metrics should be considered invalid until process restart
kgateway_routing_domains|gauge|namespace, gateway, port|Number of domains per listener
kgateway_status_syncer_status_sync_duration_seconds|histogram|name, namespace, syncer|Status sync duration
kgateway_status_syncer_status_syncs_total|counter|name, namespace, syncer, result|Total number of status syncs
kgateway_translator_translation_duration_seconds|histogram|name, namespace, translator|Translation duration
kgateway_translator_translations_running|gauge|name, namespace, translator|Current number of translations running
kgateway_translator_translations_total|counter|name, namespace, translator, result|Total number of translations
kgateway_xds_auth_rq_failure_total|counter||Total number of failed xDS auth requests
kgateway_xds_auth_rq_success_total|counter||Total number of successful xDS auth requests
kgateway_xds_auth_rq_total|counter||Total number of xDS auth requests
kgateway_xds_snapshot_resources|gauge|gateway, namespace, resource|Current number of resources in XDS snapshot
kgateway_xds_snapshot_sync_duration_seconds|histogram|gateway, namespace|Duration of time for a gateway resource update to be synced in an XDS snapshot
kgateway_xds_snapshot_syncs_total|counter|gateway, namespace|Total number of XDS snapshot syncs
kgateway_xds_snapshot_transform_duration_seconds|histogram|gateway, namespace|XDS snapshot transform duration
kgateway_xds_snapshot_transforms_total|counter|gateway, namespace, result|Total number of XDS snapshot transforms
