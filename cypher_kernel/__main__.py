from ipykernel.kernelapp import IPKernelApp
from . import CypherKernel

IPKernelApp.launch_instance(kernel_class=CypherKernel)
