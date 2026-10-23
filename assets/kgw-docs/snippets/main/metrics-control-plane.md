Name|Type|Labels|Help
--|--|--|--
kgateway_build_info|gauge|version, revision, goversion, goos, goarch|Build information of the running controller. The series always has value 1.
kgateway_controller_reconcile_duration_seconds|histogram|controller, name, namespace|Reconcile duration for controller
kgateway_controller_reconciliations_total|counter|controller, name, namespace, result|Total number of controller reconciliations
kgateway_ec2_discovery_endpoints_active|gauge|namespace, name|Current number of active Envoy endpoints discovered for an EC2 Backend
kgateway_ec2_discovery_error_state|gauge|namespace, name|Whether the most recent EC2 discovery poll for a Backend failed (1) or succeeded (0)
kgateway_ec2_discovery_poll_duration_seconds|histogram|namespace, name, result|Duration of EC2 endpoint discovery polls per Backend
kgateway_ec2_discovery_poll_total|counter|namespace, name, result, reason|Total number of EC2 endpoint discovery refresh attempts per Backend
kgateway_envoy_xds_rejects_active|gauge|gateway_namespace, gateway_name, type_url|Number of connected stream and resource type pairs with unresolved xDS rejections
kgateway_envoy_xds_rejects_total|counter|gateway_namespace, gateway_name, type_url|Total xDS rejection episodes by stream and resource type; repeated NACKs count once until a request without an error
kgateway_nack_resends_suppressed_total|counter|typeURLLabel|Number of times a NACKed xDS response was not re-sent because the snapshot had not changed
kgateway_perclient_bounded_publishes_total|counter|gatewayLabel, namespaceLabel, mode|Withheld or held per-client publications released by a time bound before every referenced cluster was ready, by mode
kgateway_perclient_defers_total|counter|gatewayLabel, namespaceLabel, reason|Per-client xDS snapshots built while a referenced cluster was not ready, by reason
kgateway_perclient_inconsistent_snapshots_total|counter||Per-client xDS snapshots that failed the pre-publication consistency check; any increment is a bug
kgateway_perclient_reclaimed_total|counter||Per-client xDS snapshot cache entries reclaimed after their client left and stayed gone for the grace period
kgateway_perclient_withheld_clients|gauge|gatewayLabel, namespaceLabel, state|Clients whose first publish on their connection is withheld until referenced clusters are ready, by state
kgateway_reconnect_responses_total|counter|typeURLLabel|Number of reconnecting proxies' first endpoint, route or secret requests whose held version was cleared, so the current or next snapshot answers them even at that version
kgateway_resources_managed|gauge|namespace, parent, resource|Current number of resources managed
kgateway_resources_updates_dropped_total|counter||Total number of xds_snapshot sync metrics updates dropped. If this metric is ever greater than 0, the xds_snapshot sync metrics should be considered invalid until process restart
kgateway_routing_domains|gauge|namespace, gateway, port|Number of domains per listener
kgateway_routing_replacements_total|counter|gateway_namespace, gateway, error_type|Number of routes, virtual hosts, or route configurations replaced with a synthetic 500 direct response due to invalid configuration detected during translation.
kgateway_status_writes_total|counter|kind, result|Total number of status write attempts by resource kind and result. result=\"error\" counts writes that failed after every retry.
kgateway_translator_translation_duration_seconds|histogram|name, namespace, translator|Translation duration
kgateway_translator_translations_total|counter|name, namespace, translator, result|Total number of translations
kgateway_validation_cache_hits_total|counter|caller|Total number of Envoy validation cache hits.
kgateway_validation_cache_misses_total|counter|caller|Total number of Envoy validation cache misses.
kgateway_validation_calls_total|counter|caller|Total number of Envoy validation requests.
kgateway_validation_duration_seconds|histogram|caller, result|Duration of Envoy validation requests.
kgateway_validation_invalid_xds_total|counter|caller|Total number of Envoy invalid-xDS validation results.
kgateway_validation_invocation_errors_total|counter|caller|Total number of Envoy validation invocation errors.
kgateway_validation_mode|gauge|mode, validator_mode|Configured validation mode. The active mode series has value 1.
kgateway_validation_valid_total|counter|caller|Total number of successful Envoy validation results.
kgateway_xds_auth_rq_failure_total|counter||Total number of failed xDS auth requests
kgateway_xds_auth_rq_success_total|counter||Total number of successful xDS auth requests
kgateway_xds_auth_rq_total|counter||Total number of xDS auth requests
kgateway_xds_cluster_scoping_disabled_gateways|gauge|gatewayLabel, namespaceLabel|Gateways with a connected proxy group whose CDS is unscoped because its configuration selects a destination at request time
kgateway_xds_cluster_scoping_dropped_clusters|gauge|gatewayLabel, namespaceLabel|Most backend clusters withheld from any of a gateway's connected proxy groups because their configuration references none of them
kgateway_xds_cluster_scoping_transitions_total|counter|gatewayLabel, namespaceLabel, transition|Clusters whose emitted-set change needed a grace window, per proxy group, by transition
kgateway_xds_snapshot_deferred_clients|gauge|gateway, namespace|Connected xDS clients whose snapshot is currently withheld because per-client inputs are not ready
kgateway_xds_snapshot_resources|gauge|gateway, namespace, resource|Current number of resources in XDS snapshot
kgateway_xds_snapshot_sync_duration_seconds|histogram|gateway, namespace|Duration of time for a gateway resource update to be synced in an XDS snapshot
kgateway_xds_snapshot_syncs_total|counter|gateway, namespace|Total number of XDS snapshot syncs
kgateway_xds_snapshot_transform_duration_seconds|histogram|gateway, namespace|XDS snapshot transform duration
kgateway_xds_snapshot_transforms_total|counter|gateway, namespace, result|Total number of XDS snapshot transforms
