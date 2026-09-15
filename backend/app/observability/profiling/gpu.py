"""
GPU Profiling Module

Tracks:
- GPU utilization
- VRAM usage
- Temperature
- Power usage
- CUDA information

Used for:
- LLM inference monitoring
- GPU cost optimization
- Model performance analysis
"""


import time
from dataclasses import dataclass
from typing import Dict, List


try:
    import pynvml

    NVML_AVAILABLE = True

except ImportError:

    NVML_AVAILABLE = False



@dataclass
class GPUStats:
    """
    GPU metrics container.
    """

    device_id: int
    name: str
    utilization: float
    memory_used_mb: float
    memory_total_mb: float
    temperature: float
    power_usage: float
    timestamp: float



class GPUProfiler:
    """
    NVIDIA GPU profiler.

    Example:

        gpu = GPUProfiler()

        print(
            gpu.snapshot()
        )
    """



    def __init__(self):

        self.enabled = False


        if NVML_AVAILABLE:

            try:

                pynvml.nvmlInit()

                self.enabled = True


            except Exception:

                self.enabled = False



    def device_count(self):

        if not self.enabled:
            return 0


        return pynvml.nvmlDeviceGetCount()



    def collect_gpu(
        self,
        device_id: int
    ) -> GPUStats:


        handle = (
            pynvml
            .nvmlDeviceGetHandleByIndex(
                device_id
            )
        )


        name = (
            pynvml
            .nvmlDeviceGetName(
                handle
            )
        )


        memory = (
            pynvml
            .nvmlDeviceGetMemoryInfo(
                handle
            )
        )


        utilization = (
            pynvml
            .nvmlDeviceGetUtilizationRates(
                handle
            )
        )


        temperature = (
            pynvml
            .nvmlDeviceGetTemperature(
                handle,
                pynvml.NVML_TEMPERATURE_GPU
            )
        )


        power = (
            pynvml
            .nvmlDeviceGetPowerUsage(
                handle
            )
            /
            1000
        )



        return GPUStats(

            device_id=device_id,

            name=name.decode()
            if isinstance(name, bytes)
            else name,


            utilization=
                utilization.gpu,


            memory_used_mb=
                memory.used /
                (1024 ** 2),


            memory_total_mb=
                memory.total /
                (1024 ** 2),


            temperature=
                temperature,


            power_usage=
                power,


            timestamp=
                time.time()
        )



    def snapshot(self) -> Dict:
        """
        Export GPU metrics.
        """

        if not self.enabled:

            return {

                "gpu":
                    None,

                "available":
                    False
            }



        devices=[]


        for i in range(
            self.device_count()
        ):

            stats = self.collect_gpu(i)


            devices.append({

                "id":
                    stats.device_id,

                "name":
                    stats.name,

                "utilization":
                    stats.utilization,

                "memory_used_mb":
                    round(
                        stats.memory_used_mb,
                        2
                    ),

                "memory_total_mb":
                    round(
                        stats.memory_total_mb,
                        2
                    ),

                "temperature":
                    stats.temperature,

                "power_watts":
                    stats.power_usage

            })



        return {

            "available":
                True,

            "gpu":
                devices,


            "timestamp":
                time.time()
        }