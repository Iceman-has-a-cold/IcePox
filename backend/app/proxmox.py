from proxmoxer import ProxmoxAPI
from .config import settings
import time

class ProxmoxManager:
    def __init__(self):
        self.proxmox = ProxmoxAPI(
            settings.proxmox_host,
            user=settings.proxmox_api_token_id.split('!')[0],
            token_name=settings.proxmox_api_token_id.split('!')[1],
            token_value=settings.proxmox_api_token_secret,
            verify_ssl=False,
            port=8006
        )

    def get_vm_status(self, vmid: str):
        try:
            node = self.proxmox.nodes.get()[0]['node']
            
            # Get basic VM status
            vm_status = self.proxmox.nodes(node).qemu(vmid).status.current.get()
            
            # Get disk info from config
            config = self.proxmox.nodes(node).qemu(vmid).config.get()
            
            # Get RRD stats
            rrd_data = self.proxmox.nodes(node).qemu(vmid).rrddata.get(
                timeframe='hour'
            )
            latest_stats = rrd_data[-1] if rrd_data else {}
            
            # Calculate total disk size from config
            disk_size = 0
            for key, value in config.items():
                if key.startswith('scsi') or key.startswith('virtio') or key.startswith('ide') or key.startswith('sata'):
                    if isinstance(value, str) and 'size=' in value:
                        size_str = value.split('size=')[1].split(',')[0]
                        if size_str.endswith('G'):
                            disk_size = float(size_str[:-1]) * 1024 * 1024 * 1024
                        elif size_str.endswith('M'):
                            disk_size = float(size_str[:-1]) * 1024 * 1024
            
            # Get historical data for graphs
            historical_data = self.proxmox.nodes(node).qemu(vmid).rrddata.get(
                timeframe='hour',
                cf='AVERAGE'  # Use AVERAGE for smoother graphs
            )
            
            return {
                "status": vm_status.get("status", "unknown"),
                "cpu": float(latest_stats.get("cpu", 0)) * 100,
                "memory": {
                    "used": int(latest_stats.get("mem", 0)),
                    "total": int(vm_status.get("maxmem", 0))
                },
                "disk": {
                    "total": int(disk_size)
                },
                "uptime": int(vm_status.get("uptime", 0)),
                "name": vm_status.get("name", f"VM {vmid}"),
                "netin": float(latest_stats.get("netin", 0)),
                "netout": float(latest_stats.get("netout", 0)),
                "historical": historical_data
            }
            
        except Exception as e:
            print(f"Error in get_vm_status: {str(e)}")
            raise e

    def reset_vm(self, vmid: str):
        try:
            node = self.proxmox.nodes.get()[0]["node"]
            result = self.proxmox.nodes(node).qemu(vmid).status.reset.post()
            return "success"
        except Exception as e:
            print(f"Error resetting VM: {str(e)}")
            raise Exception(f"Failed to reset VM: {str(e)}")

    def start_vm(self, vmid: str):
        try:
            node = self.proxmox.nodes.get()[0]["node"]
            result = self.proxmox.nodes(node).qemu(vmid).status.start.post()
            return "success"
        except Exception as e:
            raise Exception(f"Failed to start VM: {str(e)}")

    def stop_vm(self, vmid: str):
        try:
            node = self.proxmox.nodes.get()[0]["node"]
            result = self.proxmox.nodes(node).qemu(vmid).status.stop.post()
            return "success"
        except Exception as e:
            raise Exception(f"Failed to stop VM: {str(e)}")

    def shutdown_vm(self, vmid: str):
        try:
            node = self.proxmox.nodes.get()[0]["node"]
            result = self.proxmox.nodes(node).qemu(vmid).status.shutdown.post()
            return "success"
        except Exception as e:
            raise Exception(f"Failed to shutdown VM: {str(e)}")

    def get_vm_list(self):
        try:
            node = self.proxmox.nodes.get()[0]['node']
            vms = self.proxmox.nodes(node).qemu.get()
            
            vm_list = []
            for vm in vms:
                vm_list.append({
                    'vmid': vm['vmid'],
                    'name': vm['name'],
                    'status': vm['status'],
                    'cpu': vm.get('cpu', 0),
                    'memory': {
                        'used': vm.get('mem', 0),
                        'total': vm.get('maxmem', 0)
                    }
                })
            
            return vm_list
        except Exception as e:
            print(f"Error in get_vm_list: {str(e)}")
            raise e

proxmox_manager = ProxmoxManager() 