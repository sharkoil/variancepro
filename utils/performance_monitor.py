"""
Performance Monitor for Quant Commander v2.0 - Phase 3A Implementation

This module provides performance monitoring capabilities to track response times,
memory usage, and system performance metrics. It helps identify bottlenecks and
optimize the application performance.

Key Features:
- Response time tracking for analysis operations
- Memory usage monitoring
- Performance metrics collection
- Statistical analysis of performance data
- Integration with cache manager for hit/miss tracking

Author: AI Assistant
Date: July 2025
Phase: 3A - Performance Foundation
"""

import time
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from collections import defaultdict, deque
import statistics
import functools


class PerformanceMonitor:
    """
    Monitors and tracks performance metrics for Quant Commander analysis operations.
    
    This class provides comprehensive performance monitoring including response
    times, memory usage, and system resource utilization.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the performance monitor.
        
        Args:
            max_history (int): Maximum number of performance records to keep
        """
        self.max_history = max_history
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_history))
        self.lock = threading.RLock()
        self.start_time = time.time()
        
        print(f"📊 PerformanceMonitor initialized: max_history={max_history}")
    
    def record_operation(self, operation_name: str, duration: float, 
                        memory_usage: Optional[float] = None, 
                        additional_metrics: Optional[Dict] = None):
        """
        Record performance metrics for an operation.
        
        Args:
            operation_name (str): Name of the operation
            duration (float): Duration in seconds
            memory_usage (float, optional): Memory usage in MB
            additional_metrics (Dict, optional): Additional metrics to record
        """
        with self.lock:
            timestamp = time.time()
            
            # Record basic metrics
            metric_record = {
                'timestamp': timestamp,
                'duration': duration,
                'memory_usage': memory_usage or self._get_memory_usage(),
                'operation': operation_name
            }
            
            # Add additional metrics if provided
            if additional_metrics:
                metric_record.update(additional_metrics)
            
            # Store in metrics history
            self.metrics[operation_name].append(metric_record)
            self.metrics['all_operations'].append(metric_record)
            
            # Log significant performance events
            if duration > 5.0:  # Log slow operations (>5 seconds)
                print(f"⚠️ Slow operation detected: {operation_name} took {duration:.2f}s")
            elif duration > 1.0:  # Log moderately slow operations (>1 second)
                print(f"📊 Operation timing: {operation_name} took {duration:.2f}s")
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage in MB.
        
        Returns:
            float: Memory usage in MB
        """
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception as e:
            print(f"⚠️ Memory monitoring error: {str(e)}")
            return 0.0
    
    def get_operation_stats(self, operation_name: str) -> Dict:
        """
        Get statistics for a specific operation.
        
        Args:
            operation_name (str): Name of the operation
            
        Returns:
            Dict: Statistics including avg, min, max, count, etc.
        """
        with self.lock:
            if operation_name not in self.metrics or not self.metrics[operation_name]:
                return {
                    'count': 0,
                    'avg_duration': 0.0,
                    'min_duration': 0.0,
                    'max_duration': 0.0,
                    'avg_memory': 0.0,
                    'total_time': 0.0
                }
            
            records = list(self.metrics[operation_name])
            durations = [r['duration'] for r in records]
            memory_usage = [r['memory_usage'] for r in records]
            
            return {
                'count': len(records),
                'avg_duration': statistics.mean(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'median_duration': statistics.median(durations),
                'avg_memory': statistics.mean(memory_usage),
                'total_time': sum(durations),
                'last_run': datetime.fromtimestamp(records[-1]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_system_stats(self) -> Dict:
        """
        Get current system performance statistics.
        
        Returns:
            Dict: System stats including CPU, memory, and uptime
        """
        try:
            current_time = time.time()
            uptime = current_time - self.start_time
            
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'available_memory_mb': psutil.virtual_memory().available / 1024 / 1024,
                'uptime_seconds': uptime,
                'uptime_formatted': str(timedelta(seconds=int(uptime))),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            print(f"⚠️ System stats error: {str(e)}")
            return {
                'cpu_percent': 0.0,
                'memory_percent': 0.0,
                'available_memory_mb': 0.0,
                'uptime_seconds': 0.0,
                'uptime_formatted': 'Unknown',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def get_performance_summary(self) -> Dict:
        """
        Get a comprehensive performance summary.
        
        Returns:
            Dict: Summary of all performance metrics
        """
        with self.lock:
            summary = {
                'system': self.get_system_stats(),
                'operations': {},
                'top_operations': []
            }
            
            # Get stats for each operation type
            for operation_name in self.metrics.keys():
                if operation_name != 'all_operations':
                    stats = self.get_operation_stats(operation_name)
                    if stats['count'] > 0:
                        summary['operations'][operation_name] = stats
            
            # Find top operations by total time
            operation_times = []
            for op_name, stats in summary['operations'].items():
                operation_times.append((op_name, stats['total_time'], stats['count']))
            
            # Sort by total time (descending)
            operation_times.sort(key=lambda x: x[1], reverse=True)
            summary['top_operations'] = operation_times[:5]  # Top 5 operations
            
            return summary
    
    def clear_metrics(self):
        """
        Clear all performance metrics.
        """
        with self.lock:
            self.metrics.clear()
            print("🧹 Performance metrics cleared")
    
    def get_recent_operations(self, minutes: int = 5) -> List[Dict]:
        """
        Get operations from the last N minutes.
        
        Args:
            minutes (int): Number of minutes to look back
            
        Returns:
            List[Dict]: Recent operations
        """
        with self.lock:
            cutoff_time = time.time() - (minutes * 60)
            recent_ops = []
            
            for record in self.metrics['all_operations']:
                if record['timestamp'] >= cutoff_time:
                    recent_ops.append(record)
            
            return recent_ops


def performance_monitor(operation_name: str, monitor_instance: Optional[PerformanceMonitor] = None):
    """
    Decorator to automatically monitor performance of functions.
    
    Args:
        operation_name (str): Name to record for this operation
        monitor_instance (PerformanceMonitor, optional): Monitor instance to use
        
    Returns:
        Callable: Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Use global monitor if none provided
            monitor = monitor_instance or get_performance_monitor()
            
            # Record start time and memory
            start_time = time.time()
            start_memory = monitor._get_memory_usage()
            
            try:
                # Execute the function
                result = func(*args, **kwargs)
                
                # Record successful completion
                end_time = time.time()
                end_memory = monitor._get_memory_usage()
                duration = end_time - start_time
                memory_delta = end_memory - start_memory
                
                monitor.record_operation(
                    operation_name=operation_name,
                    duration=duration,
                    memory_usage=end_memory,
                    additional_metrics={
                        'memory_delta': memory_delta,
                        'status': 'success'
                    }
                )
                
                return result
                
            except Exception as e:
                # Record failed operation
                end_time = time.time()
                duration = end_time - start_time
                
                monitor.record_operation(
                    operation_name=operation_name,
                    duration=duration,
                    additional_metrics={
                        'status': 'error',
                        'error': str(e)
                    }
                )
                
                raise  # Re-raise the exception
        
        return wrapper
    return decorator


# Global performance monitor instance
_performance_monitor = None


def get_performance_monitor() -> PerformanceMonitor:
    """
    Get the global performance monitor instance (singleton pattern).
    
    Returns:
        PerformanceMonitor: The global performance monitor instance
    """
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor


def clear_performance_metrics():
    """
    Clear all performance metrics (useful for testing).
    """
    global _performance_monitor
    if _performance_monitor:
        _performance_monitor.clear_metrics()


def get_performance_summary() -> Dict:
    """
    Get global performance summary.
    
    Returns:
        Dict: Performance summary
    """
    return get_performance_monitor().get_performance_summary()
