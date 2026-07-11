from .base import oc_named, oc_simple
TOOLS={
'storage_health': oc_simple('storage_health','Resumo de storage.',['get','storageclasses,pv,pvc','-A','-o','wide']),
'pending_pvcs': oc_simple('pending_pvcs','PVCs para análise de Pending.',['get','pvc','-A','-o','wide']),
'pvc_details': oc_named('pvc_details','Detalhes de PVC.','pvc',namespaced=True),
'pv_details': oc_named('pv_details','Detalhes de PV.','pv'),
'volume_attachments': oc_simple('volume_attachments','VolumeAttachments.',['get','volumeattachments','-o','wide']),
'csi_health': oc_simple('csi_health','CSIDrivers e CSINodes.',['get','csidrivers,csinodes','-o','wide']),
}
