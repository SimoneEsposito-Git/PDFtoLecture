import os
import onnxruntime
from onnxruntime import InferenceSession, GraphOptimizationLevel

def create_session(model_path="models/kokoro-v1.0.onnx"):
    """
    Create and configure an ONNX Runtime session.

    Args:
        model_path (str): Path to the ONNX model file.

    Returns:
        InferenceSession: Configured ONNX Runtime session.
    """
    providers = onnxruntime.get_available_providers()
    print(f"Available ONNX Runtime providers: {providers}")

    # Prioritize fastest providers
    preferred_providers = []
    if 'CUDAExecutionProvider' in providers:
        preferred_providers.append('CUDAExecutionProvider')
    elif 'DnnlExecutionProvider' in providers:
        preferred_providers.append('DnnlExecutionProvider')
    elif 'CPUExecutionProvider' in providers:
        preferred_providers.append('CPUExecutionProvider')
    
    if not preferred_providers:
        preferred_providers = providers

    sess_options = onnxruntime.SessionOptions()

    # Set optimization level to maximum
    sess_options.graph_optimization_level = GraphOptimizationLevel.ORT_ENABLE_ALL

    # Optimize threading based on CPU
    cpu_count = os.cpu_count()
    print(f"Setting threads to CPU cores count: {cpu_count}")
    sess_options.intra_op_num_threads = cpu_count
    sess_options.inter_op_num_threads = 1

    # Enable memory optimizations
    sess_options.enable_mem_pattern = True
    sess_options.enable_cpu_mem_arena = True

    # Create and return the session
    session = InferenceSession(
        model_path, providers=preferred_providers, sess_options=sess_options
    )
    return session