import time
import tracemalloc
from contextlib import contextmanager
from utils.logger import get_logger


logger = get_logger()

@contextmanager
def profile_block(label="block"):
    """
    Context manager para medir tempo e memória de um bloco de código.
    """
    tracemalloc.start()
    start_time = time.perf_counter()
    try:
        yield
    finally:
        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        duration_ms = round((end_time - start_time) * 1000, 2)
        logger.info({
            "message": f"PROFILING: {label}",
            "duration_ms": duration_ms,
            "memory_current_kb": round(current / 1024, 2),
            "memory_peak_kb": round(peak / 1024, 2),
        })

