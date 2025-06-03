"""
AI Analytics and Monitoring Module

This module provides comprehensive analytics and monitoring capabilities
for AI operations in the insurance system.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class AIMetrics:
    """AI performance metrics."""
    provider: str
    model: str
    operation: str
    response_time: float
    success: bool
    error: Optional[str] = None
    token_usage: Optional[Dict[str, int]] = None
    confidence_score: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AIAnalytics:
    """AI analytics summary."""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    average_confidence: float = 0.0
    provider_stats: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    error_stats: Dict[str, int] = field(default_factory=dict)
    hourly_stats: Dict[str, int] = field(default_factory=dict)

class AIMonitor:
    """AI monitoring and analytics service."""
    
    def __init__(self, max_metrics_history: int = 10000):
        self.metrics_history: deque = deque(maxlen=max_metrics_history)
        self.real_time_stats = defaultdict(list)
        self.provider_performance = defaultdict(lambda: defaultdict(list))
        self.error_tracking = defaultdict(int)
        self.start_time = datetime.utcnow()
        
    def record_ai_operation(
        self,
        provider: str,
        model: str,
        operation: str,
        response_time: float,
        success: bool,
        error: Optional[str] = None,
        token_usage: Optional[Dict[str, int]] = None,
        confidence_score: Optional[float] = None
    ) -> None:
        """Record an AI operation for analytics."""
        metrics = AIMetrics(
            provider=provider,
            model=model,
            operation=operation,
            response_time=response_time,
            success=success,
            error=error,
            token_usage=token_usage,
            confidence_score=confidence_score
        )
        
        self.metrics_history.append(metrics)
        self._update_real_time_stats(metrics)
        
    def _update_real_time_stats(self, metrics: AIMetrics) -> None:
        """Update real-time statistics."""
        # Provider performance tracking
        self.provider_performance[metrics.provider]['response_times'].append(metrics.response_time)
        self.provider_performance[metrics.provider]['success_rate'].append(metrics.success)
        
        if metrics.confidence_score:
            self.provider_performance[metrics.provider]['confidence_scores'].append(metrics.confidence_score)
        
        # Error tracking
        if not metrics.success and metrics.error:
            self.error_tracking[metrics.error] += 1
        
        # Keep only recent data for real-time stats (last 100 operations)
        for provider_stats in self.provider_performance.values():
            for stat_list in provider_stats.values():
                if len(stat_list) > 100:
                    stat_list.pop(0)
    
    def get_analytics_summary(self, hours_back: int = 24) -> AIAnalytics:
        """Get comprehensive analytics summary."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        if not recent_metrics:
            return AIAnalytics()
        
        total_requests = len(recent_metrics)
        successful_requests = sum(1 for m in recent_metrics if m.success)
        failed_requests = total_requests - successful_requests
        
        response_times = [m.response_time for m in recent_metrics]
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        total_tokens = sum(
            (m.token_usage.get('total_tokens', 0) if m.token_usage else 0)
            for m in recent_metrics
        )
        
        confidence_scores = [m.confidence_score for m in recent_metrics if m.confidence_score]
        average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        # Provider statistics
        provider_stats = {}
        for provider in set(m.provider for m in recent_metrics):
            provider_metrics = [m for m in recent_metrics if m.provider == provider]
            provider_stats[provider] = {
                'requests': len(provider_metrics),
                'success_rate': sum(1 for m in provider_metrics if m.success) / len(provider_metrics),
                'avg_response_time': sum(m.response_time for m in provider_metrics) / len(provider_metrics),
                'total_tokens': sum(
                    (m.token_usage.get('total_tokens', 0) if m.token_usage else 0)
                    for m in provider_metrics
                )
            }
        
        # Error statistics
        error_stats = defaultdict(int)
        for m in recent_metrics:
            if not m.success and m.error:
                error_stats[m.error] += 1
        
        # Hourly statistics
        hourly_stats = defaultdict(int)
        for m in recent_metrics:
            hour_key = m.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_stats[hour_key] += 1
        
        return AIAnalytics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=average_response_time,
            total_tokens_used=total_tokens,
            average_confidence=average_confidence,
            provider_stats=dict(provider_stats),
            error_stats=dict(error_stats),
            hourly_stats=dict(hourly_stats)
        )
    
    def get_provider_comparison(self) -> Dict[str, Dict[str, float]]:
        """Get performance comparison between providers."""
        comparison = {}
        
        for provider, stats in self.provider_performance.items():
            if stats['response_times'] and stats['success_rate']:
                avg_response_time = sum(stats['response_times']) / len(stats['response_times'])
                success_rate = sum(stats['success_rate']) / len(stats['success_rate'])
                avg_confidence = (
                    sum(stats['confidence_scores']) / len(stats['confidence_scores'])
                    if stats['confidence_scores'] else 0
                )
                
                comparison[provider] = {
                    'avg_response_time': avg_response_time,
                    'success_rate': success_rate,
                    'avg_confidence': avg_confidence,
                    'total_operations': len(stats['response_times'])
                }
        
        return comparison
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Get detailed error analysis."""
        recent_errors = [
            m for m in self.metrics_history 
            if not m.success and m.timestamp >= datetime.utcnow() - timedelta(hours=24)
        ]
        
        error_by_provider = defaultdict(lambda: defaultdict(int))
        error_by_operation = defaultdict(lambda: defaultdict(int))
        
        for error_metric in recent_errors:
            error_by_provider[error_metric.provider][error_metric.error] += 1
            error_by_operation[error_metric.operation][error_metric.error] += 1
        
        return {
            'total_errors_24h': len(recent_errors),
            'error_rate_24h': len(recent_errors) / len(self.metrics_history) if self.metrics_history else 0,
            'errors_by_provider': dict(error_by_provider),
            'errors_by_operation': dict(error_by_operation),
            'most_common_errors': dict(sorted(
                self.error_tracking.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
        }
    
    def get_performance_trends(self, hours_back: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """Get performance trends over time."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        recent_metrics = [m for m in self.metrics_history if m.timestamp >= cutoff_time]
        
        # Group by hour
        hourly_data = defaultdict(lambda: {
            'response_times': [],
            'success_count': 0,
            'total_count': 0,
            'confidence_scores': []
        })
        
        for metric in recent_metrics:
            hour_key = metric.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_data[hour_key]['response_times'].append(metric.response_time)
            hourly_data[hour_key]['total_count'] += 1
            if metric.success:
                hourly_data[hour_key]['success_count'] += 1
            if metric.confidence_score:
                hourly_data[hour_key]['confidence_scores'].append(metric.confidence_score)
        
        # Calculate trends
        trends = []
        for hour, data in sorted(hourly_data.items()):
            avg_response_time = sum(data['response_times']) / len(data['response_times']) if data['response_times'] else 0
            success_rate = data['success_count'] / data['total_count'] if data['total_count'] > 0 else 0
            avg_confidence = sum(data['confidence_scores']) / len(data['confidence_scores']) if data['confidence_scores'] else 0
            
            trends.append({
                'hour': hour,
                'avg_response_time': avg_response_time,
                'success_rate': success_rate,
                'avg_confidence': avg_confidence,
                'total_requests': data['total_count']
            })
        
        return {'hourly_trends': trends}
    
    def get_model_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics by model."""
        model_stats = defaultdict(lambda: {
            'response_times': [],
            'success_count': 0,
            'total_count': 0,
            'confidence_scores': [],
            'token_usage': []
        })
        
        for metric in self.metrics_history:
            model_key = f"{metric.provider}:{metric.model}"
            model_stats[model_key]['response_times'].append(metric.response_time)
            model_stats[model_key]['total_count'] += 1
            if metric.success:
                model_stats[model_key]['success_count'] += 1
            if metric.confidence_score:
                model_stats[model_key]['confidence_scores'].append(metric.confidence_score)
            if metric.token_usage:
                model_stats[model_key]['token_usage'].append(metric.token_usage.get('total_tokens', 0))
        
        # Calculate summary statistics
        summary = {}
        for model, stats in model_stats.items():
            if stats['total_count'] > 0:
                summary[model] = {
                    'avg_response_time': sum(stats['response_times']) / len(stats['response_times']),
                    'success_rate': stats['success_count'] / stats['total_count'],
                    'avg_confidence': (
                        sum(stats['confidence_scores']) / len(stats['confidence_scores'])
                        if stats['confidence_scores'] else 0
                    ),
                    'avg_tokens': (
                        sum(stats['token_usage']) / len(stats['token_usage'])
                        if stats['token_usage'] else 0
                    ),
                    'total_requests': stats['total_count']
                }
        
        return summary
    
    def export_metrics(self, format: str = 'json') -> str:
        """Export metrics in specified format."""
        analytics = self.get_analytics_summary()
        
        if format.lower() == 'json':
            return json.dumps({
                'analytics_summary': analytics.__dict__,
                'provider_comparison': self.get_provider_comparison(),
                'error_analysis': self.get_error_analysis(),
                'performance_trends': self.get_performance_trends(),
                'model_performance': self.get_model_performance(),
                'export_timestamp': datetime.utcnow().isoformat()
            }, indent=2, default=str)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def clear_old_metrics(self, days_to_keep: int = 7) -> int:
        """Clear metrics older than specified days."""
        cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
        original_count = len(self.metrics_history)
        
        # Filter out old metrics
        self.metrics_history = deque(
            [m for m in self.metrics_history if m.timestamp >= cutoff_time],
            maxlen=self.metrics_history.maxlen
        )
        
        cleared_count = original_count - len(self.metrics_history)
        logger.info(f"Cleared {cleared_count} old metrics (older than {days_to_keep} days)")
        
        return cleared_count

# Global AI monitor instance
ai_monitor = AIMonitor()

def get_ai_monitor() -> AIMonitor:
    """Get the global AI monitor instance."""
    return ai_monitor

class AIPerformanceTracker:
    """Context manager for tracking AI operation performance."""
    
    def __init__(
        self,
        provider: str,
        model: str,
        operation: str,
        monitor: Optional[AIMonitor] = None
    ):
        self.provider = provider
        self.model = model
        self.operation = operation
        self.monitor = monitor or get_ai_monitor()
        self.start_time = None
        self.success = False
        self.error = None
        self.token_usage = None
        self.confidence_score = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            response_time = time.time() - self.start_time
            self.success = exc_type is None
            if exc_val:
                self.error = str(exc_val)
            
            self.monitor.record_ai_operation(
                provider=self.provider,
                model=self.model,
                operation=self.operation,
                response_time=response_time,
                success=self.success,
                error=self.error,
                token_usage=self.token_usage,
                confidence_score=self.confidence_score
            )
    
    def set_token_usage(self, token_usage: Dict[str, int]) -> None:
        """Set token usage for this operation."""
        self.token_usage = token_usage
    
    def set_confidence_score(self, confidence_score: float) -> None:
        """Set confidence score for this operation."""
        self.confidence_score = confidence_score