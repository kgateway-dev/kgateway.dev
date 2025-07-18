Name|Type|Labels|Help
--|--|--|--
kgateway_controller_reconcile_duration_seconds|histogram|controller|Reconcile duration for controller
kgateway_controller_reconciliations_running|gauge|controller|Number of reconciliations currently running
kgateway_controller_reconciliations_total|counter|controller, result|Total number of controller reconciliations
kgateway_resources_managed|gauge|namespace, parent, resource|Current number of resources managed
kgateway_resources_status_sync_duration_seconds|histogram|gateway, namespace, resource|Duration of time for a resource update to receive a status report
kgateway_resources_status_syncs_completed_total|counter|gateway, namespace, resource|Total number of status syncs completed for resources
kgateway_resources_syncs_started_total|counter|gateway, namespace, resource|Total number of syncs started
kgateway_resources_updates_dropped_total|counter||Total number of resources metrics updates dropped. If this metric is ever greater than 0, all resources subsystem metrics should be considered invalid until process restart
kgateway_resources_xds_snapshot_sync_duration_seconds|histogram|gateway, namespace, resource|Duration of time for a resource update to be synced in XDS snapshots
kgateway_resources_xds_snapshot_syncs_total|counter|gateway, namespace, resource|Total number of XDS snapshot syncs for resources
kgateway_routing_domains|gauge|namespace, gateway, port|Number of domains per listener
kgateway_status_syncer_status_sync_duration_seconds|histogram|syncer|Status sync duration
kgateway_status_syncer_status_syncs_total|counter|syncer, result|Total number of status syncs
kgateway_translator_translation_duration_seconds|histogram|translator|Translation duration
kgateway_translator_translations_running|gauge|translator|Current number of translations running
kgateway_translator_translations_total|counter|translator, result|Total number of translations
kgateway_xds_snapshot_resources|gauge|gateway, namespace, resource|Current number of resources in XDS snapshot
kgateway_xds_snapshot_syncs_total|counter|gateway, namespace|Total number of XDS snapshot syncs
kgateway_xds_snapshot_transform_duration_seconds|histogram|gateway, namespace|XDS snapshot transform duration
kgateway_xds_snapshot_transforms_total|counter|gateway, namespace, result|Total number of XDS snapshot transforms