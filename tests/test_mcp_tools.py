import unittest
from mcp_server.tools import get_tool_registry, list_tools
REQUIRED={'list_configured_clusters','current_context','select_cluster_context','validate_cluster_context','cluster_identity','check_permissions','cluster_version','cluster_infrastructure','cluster_health','cluster_operators','degraded_operators','progressing_operators','recent_warning_events','resource_usage','cluster_capacity','upgrade_status','list_nodes','unhealthy_nodes','node_details','node_resource_usage','node_pods','machineconfigpool_health','unhealthy_pods','restarting_pods','pending_pods','pod_details','pod_logs','pod_previous_logs','pod_events','workload_health','deployment_health','statefulset_health','daemonset_health','failed_jobs','namespace_health','namespace_events','namespace_resource_usage','namespace_quotas','operator_details','operator_related_resources','operator_namespace_health','olm_health','subscription_details','csv_details','installplan_details','catalogsource_health','storage_health','pending_pvcs','pvc_details','pv_details','volume_attachments','csi_health','network_health','ingress_health','dns_health','route_health','service_health','endpoints_health','network_policies','api_health','etcd_health','authentication_health','monitoring_health','console_health','image_registry_health','certificate_health','pending_csrs','collect_cluster_evidence','collect_namespace_evidence','collect_pod_evidence','collect_workload_evidence','collect_operator_evidence','collect_node_evidence','collect_storage_evidence','collect_network_evidence','generate_evidence_manifest','sanitize_evidence','package_evidence','generate_base_report','generate_incident_timeline','compare_evidence_collections','compare_cluster_health'}
class McpToolsTests(unittest.TestCase):
    def test_required_tools_exist(self):
        self.assertTrue(REQUIRED.issubset(set(get_tool_registry())))
    def test_no_generic_terminal_tool(self):
        names={item['name'] for item in list_tools()}
        forbidden={'execute_command','execute_shell','run_command','run_oc','run_kubectl','run_bash','terminal','shell'}
        self.assertFalse(names & forbidden)
if __name__ == '__main__': unittest.main()
