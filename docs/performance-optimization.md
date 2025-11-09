# Performance Optimization Guide

This guide provides comprehensive best practices and techniques for optimizing performance in Symphonic-Joules applications.

## 🎯 Overview

Performance optimization is crucial when working with audio processing and energy calculations, as these operations can be computationally intensive. This guide covers strategies for optimizing:

- Memory usage
- CPU utilization
- I/O operations
- Algorithm efficiency
- Caching strategies

## 🚀 Quick Wins

### 1. Avoid Mutable Default Arguments

**Problem**: Python's mutable default arguments are evaluated once at function definition, not each call.

```python
# ❌ BAD: Mutable default argument
def process_features(signal, features=[]):
    features.append(extract_energy(signal))
    return features  # Same list is shared across all calls!

# ✅ GOOD: Use None and create new list
def process_features(signal, features=None):
    if features is None:
        features = []
    features.append(extract_energy(signal))
    return features
```

### 2. Use List Comprehensions

```python
# ❌ BAD: Appending in loop
result = []
for x in data:
    result.append(x ** 2)

# ✅ GOOD: List comprehension (faster)
result = [x ** 2 for x in data]

# ✅ BETTER: NumPy vectorization (fastest)
import numpy as np
result = np.array(data) ** 2
```

### 3. Avoid String Concatenation in Loops

```python
# ❌ BAD: String concatenation in loop
output = ""
for item in items:
    output += str(item) + "\n"  # Creates new string each iteration

# ✅ GOOD: Join method
output = "\n".join(str(item) for item in items)
```

## 💾 Memory Optimization

### Stream Processing for Large Files

Process data in chunks to avoid loading entire files into memory:

```python
def process_large_audio_file(file_path, chunk_size=8192):
    """
    Process audio file in chunks to minimize memory usage.
    
    Args:
        file_path: Path to audio file
        chunk_size: Number of samples per chunk
        
    Yields:
        Processed audio chunks
    """
    import wave
    
    with wave.open(file_path, 'rb') as audio:
        frames_remaining = audio.getnframes()
        
        while frames_remaining > 0:
            frames_to_read = min(chunk_size, frames_remaining)
            chunk = audio.readframes(frames_to_read)
            
            # Process chunk
            processed_chunk = apply_processing(chunk)
            yield processed_chunk
            
            frames_remaining -= frames_to_read

# Usage
for chunk in process_large_audio_file('large_audio.wav'):
    write_output(chunk)
```

### Memory Pooling

Reuse memory allocations to reduce garbage collection overhead:

```python
import numpy as np

class AudioBufferPool:
    """Pool of reusable audio buffers."""
    
    def __init__(self, buffer_size, num_buffers=10):
        self.pool = [np.zeros(buffer_size, dtype=np.float32) 
                     for _ in range(num_buffers)]
        self.available = list(range(num_buffers))
    
    def acquire(self):
        """Get a buffer from the pool."""
        if not self.available:
            # Pool exhausted, create temporary buffer
            return np.zeros(self.pool[0].shape, dtype=np.float32)
        
        idx = self.available.pop()
        return self.pool[idx], idx
    
    def release(self, idx):
        """Return buffer to the pool."""
        if idx < len(self.pool):
            self.available.append(idx)
            # Clear the buffer
            self.pool[idx].fill(0)

# Usage
pool = AudioBufferPool(buffer_size=4096, num_buffers=10)
buffer, idx = pool.acquire()
try:
    # Use buffer
    process_audio(buffer)
finally:
    pool.release(idx)
```

### Use Generators for Large Datasets

```python
# ❌ BAD: Loads all data into memory
def load_all_audio_files(directory):
    return [load_audio(f) for f in get_files(directory)]

# ✅ GOOD: Generator yields one at a time
def load_audio_files_generator(directory):
    for f in get_files(directory):
        yield load_audio(f)

# Usage
for audio in load_audio_files_generator('./data'):
    process(audio)  # Only one file in memory at a time
```

## ⚡ Computational Optimization

### Vectorization with NumPy

Replace Python loops with vectorized NumPy operations:

```python
import numpy as np

# ❌ BAD: Python loops (slow)
def calculate_energy_slow(signal):
    total = 0
    for sample in signal:
        total += sample ** 2
    return total / len(signal)

# ✅ GOOD: NumPy vectorization (10-100x faster)
def calculate_energy_fast(signal):
    signal_array = np.array(signal, dtype=np.float32)
    return np.mean(signal_array ** 2)

# ✅ BETTER: Pre-allocated NumPy array
def calculate_energy_fastest(signal_array):
    """Assumes signal_array is already a NumPy array."""
    return np.mean(signal_array ** 2)
```

### Use Built-in Functions

```python
# ❌ BAD: Manual implementation
def find_maximum(values):
    max_val = values[0]
    for val in values[1:]:
        if val > max_val:
            max_val = val
    return max_val

# ✅ GOOD: Built-in function (optimized in C)
def find_maximum(values):
    return max(values)

# ✅ BETTER: NumPy for numerical arrays
import numpy as np
def find_maximum(values):
    return np.max(values)
```

### Avoid Repeated Function Calls

```python
# ❌ BAD: Repeated function calls
for i in range(len(data)):
    process(data[i])

# ✅ GOOD: Cache function result
data_len = len(data)
for i in range(data_len):
    process(data[i])

# ✅ BETTER: Direct iteration (no index needed)
for item in data:
    process(item)
```

## 🔄 Caching Strategies

### Function Result Caching

Use `functools.lru_cache` for expensive computations:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=128)
def compute_fft(audio_hash, fft_size):
    """
    Compute FFT with caching.
    
    Note: audio_hash is used because audio_data itself
    isn't hashable. Generate hash from audio data.
    """
    audio_data = retrieve_audio(audio_hash)
    return np.fft.fft(audio_data, n=fft_size)

def get_audio_hash(audio_data):
    """Generate hash for audio data."""
    return hashlib.sha256(audio_data.tobytes()).hexdigest()

# Usage
audio_hash = get_audio_hash(my_audio)
spectrum = compute_fft(audio_hash, 2048)  # Cached on subsequent calls
```

### Custom Cache Implementation

For more control over caching behavior:

```python
import time
from collections import OrderedDict

class TTLCache:
    """Time-to-live cache with size limit."""
    
    def __init__(self, maxsize=128, ttl=300):
        self.cache = OrderedDict()
        self.maxsize = maxsize
        self.ttl = ttl  # seconds
    
    def get(self, key):
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return value
            else:
                # Expired
                del self.cache[key]
        return None
    
    def set(self, key, value):
        # Remove oldest if at capacity
        if len(self.cache) >= self.maxsize:
            self.cache.popitem(last=False)
        
        self.cache[key] = (value, time.time())

# Usage
feature_cache = TTLCache(maxsize=100, ttl=600)

def extract_features_cached(audio_id):
    cached = feature_cache.get(audio_id)
    if cached is not None:
        return cached
    
    features = expensive_feature_extraction(audio_id)
    feature_cache.set(audio_id, features)
    return features
```

## 🔀 Parallel Processing

### Multiprocessing for CPU-Bound Tasks

```python
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import numpy as np

def process_audio_file(file_path):
    """Process a single audio file."""
    audio = load_audio(file_path)
    features = extract_features(audio)
    energy = calculate_energy(audio)
    return {'file': file_path, 'features': features, 'energy': energy}

def process_audio_files_parallel(file_paths):
    """Process multiple audio files in parallel."""
    num_workers = multiprocessing.cpu_count()
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_audio_file, file_paths))
    
    return results

# Usage
files = ['audio1.wav', 'audio2.wav', 'audio3.wav']
results = process_audio_files_parallel(files)
```

### Threading for I/O-Bound Tasks

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def download_audio_file(url):
    """Download audio file from URL."""
    response = requests.get(url)
    return response.content

def download_files_concurrent(urls):
    """Download multiple files concurrently."""
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(download_audio_file, urls))
    return results
```

### Batch Processing

Process data in batches for better throughput:

```python
def process_in_batches(data, batch_size=100):
    """Process data in batches for better performance."""
    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]
        # Process entire batch at once
        results = process_batch(batch)
        yield from results

# Example: Batch FFT computation
import numpy as np

def batch_fft(signals, fft_size=2048):
    """Compute FFT for multiple signals at once."""
    # Stack signals into 2D array
    signal_matrix = np.vstack(signals)
    # Batch FFT (more efficient than individual FFTs)
    return np.fft.fft(signal_matrix, n=fft_size, axis=1)
```

## 📊 Profiling and Measurement

### Timing Functions

```python
import time
from functools import wraps

def timing_decorator(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.4f} seconds")
        return result
    return wrapper

@timing_decorator
def process_audio(file_path):
    # Your code here
    pass
```

### Memory Profiling

```python
import tracemalloc

def profile_memory(func):
    """Decorator to measure memory usage."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"{func.__name__} - Current: {current / 1024 / 1024:.2f} MB, "
              f"Peak: {peak / 1024 / 1024:.2f} MB")
        return result
    return wrapper

@profile_memory
def load_large_file(file_path):
    # Your code here
    pass
```

### CPU Profiling with cProfile

```python
import cProfile
import pstats

def profile_code(func):
    """Profile function with cProfile."""
    profiler = cProfile.Profile()
    profiler.enable()
    result = func()
    profiler.disable()
    
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions
    
    return result
```

## 🎨 Data Structure Selection

### Choose the Right Structure

```python
# Membership testing
# ❌ BAD: List - O(n)
if item in my_list:
    pass

# ✅ GOOD: Set - O(1)
if item in my_set:
    pass

# FIFO operations
# ❌ BAD: List with pop(0) - O(n)
queue = []
queue.append(item)
first = queue.pop(0)

# ✅ GOOD: Deque - O(1)
from collections import deque
queue = deque()
queue.append(item)
first = queue.popleft()

# Counting occurrences
# ❌ BAD: Manual counting
counts = {}
for item in data:
    counts[item] = counts.get(item, 0) + 1

# ✅ GOOD: Counter
from collections import Counter
counts = Counter(data)
```

## 🔍 Algorithm Complexity

### Optimize Algorithm Choice

```python
# Searching
# ❌ BAD: Linear search in unsorted list - O(n)
def find_item(items, target):
    for item in items:
        if item == target:
            return item
    return None

# ✅ GOOD: Binary search in sorted list - O(log n)
import bisect
def find_item_fast(sorted_items, target):
    idx = bisect.bisect_left(sorted_items, target)
    if idx < len(sorted_items) and sorted_items[idx] == target:
        return sorted_items[idx]
    return None

# Sorting
# ❌ BAD: Bubble sort - O(n²)
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr

# ✅ GOOD: Built-in sort - O(n log n)
def efficient_sort(arr):
    return sorted(arr)
```

## 🧹 Resource Management

### Use Context Managers

```python
# ❌ BAD: Manual resource management
def process_file(path):
    f = open(path)
    data = f.read()
    # If exception occurs, file may not close
    f.close()
    return process(data)

# ✅ GOOD: Context manager ensures cleanup
def process_file(path):
    with open(path) as f:
        data = f.read()
    return process(data)  # File automatically closed

# Custom context manager for resources
class AudioProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = None
    
    def __enter__(self):
        self.file = open(self.file_path, 'rb')
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
    
    def read_chunk(self, size):
        return self.file.read(size)

# Usage
with AudioProcessor('audio.wav') as processor:
    chunk = processor.read_chunk(1024)
# File automatically closed
```

## 🎯 Best Practices Summary

### Do's ✅

1. **Use NumPy** for numerical operations
2. **Profile first** - measure before optimizing
3. **Use generators** for large datasets
4. **Cache expensive** computations
5. **Process in chunks** for large files
6. **Use appropriate** data structures
7. **Parallelize** independent operations
8. **Use context managers** for resource cleanup
9. **Prefer built-in** functions and libraries
10. **Vectorize** operations when possible

### Don'ts ❌

1. **Don't use** mutable default arguments
2. **Don't concatenate** strings in loops
3. **Don't load** entire large files into memory
4. **Don't use** O(n²) algorithms when O(n log n) exists
5. **Don't optimize** without profiling first
6. **Don't ignore** memory usage
7. **Don't repeat** expensive computations
8. **Don't use** Python loops for numerical operations
9. **Don't forget** to close resources
10. **Don't sacrifice** readability for minor gains

## 📚 Additional Resources

- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)
- [NumPy Performance](https://numpy.org/doc/stable/user/basics.performance.html)
- [SciPy Optimization](https://scipy-lectures.org/advanced/optimizing/)
- [Profiling Python Code](https://docs.python.org/3/library/profile.html)

---

*Performance is a feature. Design for it from the start.*
