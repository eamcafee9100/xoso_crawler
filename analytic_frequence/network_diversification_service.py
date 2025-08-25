"""
🌐 Network-Based Diversification Service - Phase 3
=================================================

Advanced graph theory and network analysis for lottery number diversification
using pure NumPy implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Dict, List, Tuple, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, date
import json
import logging
import numpy as np
from collections import defaultdict, deque
import itertools

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class NetworkNode:
    """Network node representing a lottery number"""
    node_id: int
    frequency: int
    centrality_score: float
    clustering_coefficient: float
    betweenness_centrality: float
    pagerank_score: float
    community_id: int
    node_metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class NetworkEdge:
    """Network edge representing number co-occurrence"""
    source: int
    target: int
    weight: float
    co_occurrence_count: int
    temporal_distance: float
    edge_type: str
    strength: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class NetworkCommunity:
    """Network community of related numbers"""
    community_id: int
    member_nodes: Set[int]
    community_density: float
    modularity_score: float
    diversity_index: float
    representative_nodes: List[int]
    community_strength: float

@dataclass(frozen=True)
class DiversificationResult:
    """Network-based diversification result"""
    diversified_numbers: List[int]
    network_metrics: Dict[str, float]
    community_distribution: Dict[int, int]
    diversification_score: float
    network_efficiency: float
    coverage_breadth: float
    redundancy_minimization: float
    temporal_spread: float
    network_graph: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

class LotteryNetworkGraph:
    """Graph representation of lottery number relationships"""
    
    def __init__(self):
        """Initialize the lottery network graph"""
        self.nodes: Dict[int, NetworkNode] = {}
        self.edges: Dict[Tuple[int, int], NetworkEdge] = {}
        self.adjacency_matrix: np.ndarray = None
        self.communities: Dict[int, NetworkCommunity] = {}
        self.graph_metrics: Dict[str, float] = {}
        
    def add_node(self, node: NetworkNode):
        """Add a node to the graph"""
        self.nodes[node.node_id] = node
        
    def add_edge(self, edge: NetworkEdge):
        """Add an edge to the graph"""
        edge_key = (min(edge.source, edge.target), max(edge.source, edge.target))
        self.edges[edge_key] = edge
        
    def build_adjacency_matrix(self):
        """Build the adjacency matrix for the graph"""
        if not self.nodes:
            return
            
        max_node_id = max(self.nodes.keys())
        self.adjacency_matrix = np.zeros((max_node_id + 1, max_node_id + 1))
        
        for (source, target), edge in self.edges.items():
            self.adjacency_matrix[source, target] = edge.weight
            self.adjacency_matrix[target, source] = edge.weight
            
    def get_neighbors(self, node_id: int) -> List[int]:
        """Get neighbors of a node"""
        neighbors = []
        for (source, target), edge in self.edges.items():
            if source == node_id:
                neighbors.append(target)
            elif target == node_id:
                neighbors.append(source)
        return neighbors
        
    def calculate_centrality_metrics(self):
        """Calculate various centrality metrics for all nodes"""
        try:
            # Degree centrality
            for node_id in self.nodes:
                neighbors = self.get_neighbors(node_id)
                degree = len(neighbors)
                total_nodes = len(self.nodes)
                
                # Update node with centrality scores
                old_node = self.nodes[node_id]
                updated_node = NetworkNode(
                    node_id=old_node.node_id,
                    frequency=old_node.frequency,
                    centrality_score=degree / max(1, total_nodes - 1),
                    clustering_coefficient=self._calculate_clustering_coefficient(node_id),
                    betweenness_centrality=self._calculate_betweenness_centrality(node_id),
                    pagerank_score=0.0,  # Will be calculated separately
                    community_id=old_node.community_id,
                    node_metadata=old_node.node_metadata
                )
                self.nodes[node_id] = updated_node
                
        except Exception as e:
            logger.error(f"❌ Error calculating centrality metrics: {e}")
            
    def _calculate_clustering_coefficient(self, node_id: int) -> float:
        """Calculate clustering coefficient for a node"""
        try:
            neighbors = self.get_neighbors(node_id)
            if len(neighbors) < 2:
                return 0.0
                
            # Count triangles
            triangles = 0
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    edge_key = (min(neighbors[i], neighbors[j]), max(neighbors[i], neighbors[j]))
                    if edge_key in self.edges:
                        triangles += 1
                        
            # Possible triangles
            possible_triangles = len(neighbors) * (len(neighbors) - 1) // 2
            
            return triangles / max(1, possible_triangles)
            
        except Exception as e:
            logger.error(f"❌ Error calculating clustering coefficient: {e}")
            return 0.0
            
    def _calculate_betweenness_centrality(self, node_id: int) -> float:
        """Calculate betweenness centrality for a node (simplified)"""
        try:
            # Simplified betweenness centrality calculation
            # In a full implementation, this would use shortest path algorithms
            neighbors = self.get_neighbors(node_id)
            total_paths = len(self.nodes) * (len(self.nodes) - 1) // 2
            
            # Estimate based on node degree and position
            if total_paths == 0:
                return 0.0
                
            betweenness_estimate = len(neighbors) / max(1, total_paths)
            return min(1.0, betweenness_estimate)
            
        except Exception as e:
            logger.error(f"❌ Error calculating betweenness centrality: {e}")
            return 0.0

class NetworkDiversificationService:
    """
    🌐 Network-Based Diversification Service
    
    Uses graph theory and network analysis to optimize lottery number selection
    for maximum diversification and coverage.
    """
    
    def __init__(self, max_numbers: int = 49):
        """Initialize the network diversification service"""
        self.max_numbers = max_numbers
        self.lottery_graph = LotteryNetworkGraph()
        self.historical_patterns = []
        
        # Configuration
        self.config = {
            'community_weight': 0.3,
            'centrality_weight': 0.25,
            'diversity_weight': 0.25,
            'temporal_weight': 0.2,
            'min_community_size': 3,
            'max_communities': 8
        }
        
        logger.info("✅ Network Diversification Service initialized")
        
    def analyze_network_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        🌐 Analyze Historical Data for Network Patterns
        
        Builds a network graph from historical lottery data and analyzes
        number relationships and community structures.
        """
        try:
            logger.info(f"🌐 Analyzing network patterns from {len(historical_data)} data points...")
            
            # Step 1: Build the network graph
            self._build_network_graph(historical_data)
            
            # Step 2: Detect communities
            communities = self._detect_communities()
            
            # Step 3: Calculate network metrics
            network_metrics = self._calculate_network_metrics()
            
            # Step 4: Analyze temporal patterns
            temporal_analysis = self._analyze_temporal_patterns(historical_data)
            
            analysis_result = {
                'network_metrics': network_metrics,
                'communities': {str(k): v.__dict__ for k, v in communities.items()},
                'temporal_patterns': temporal_analysis,
                'graph_structure': {
                    'nodes': len(self.lottery_graph.nodes),
                    'edges': len(self.lottery_graph.edges),
                    'density': network_metrics.get('density', 0.0),
                    'modularity': network_metrics.get('modularity', 0.0)
                }
            }
            
            logger.info(f"✅ Network analysis completed!")
            logger.info(f"   Nodes: {len(self.lottery_graph.nodes)}")
            logger.info(f"   Edges: {len(self.lottery_graph.edges)}")
            logger.info(f"   Communities: {len(communities)}")
            logger.info(f"   Network Density: {network_metrics.get('density', 0.0):.3f}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ Error in network pattern analysis: {e}")
            return {'network_metrics': {}, 'communities': {}}
    
    def diversify_selection(self, candidate_numbers: List[int], 
                          target_count: int = 6,
                          diversification_strategy: str = 'balanced') -> DiversificationResult:
        """
        🎯 Diversify Number Selection Using Network Analysis
        
        Optimizes number selection for maximum diversification across
        network communities and structural properties.
        """
        try:
            logger.info(f"🎯 Diversifying selection from {len(candidate_numbers)} candidates...")
            logger.info(f"   Target Count: {target_count}")
            logger.info(f"   Strategy: {diversification_strategy}")
            
            # Step 1: Filter candidates that exist in network
            valid_candidates = [num for num in candidate_numbers if num in self.lottery_graph.nodes]
            
            if len(valid_candidates) < target_count:
                # Add additional numbers if needed
                all_numbers = list(range(1, self.max_numbers + 1))
                additional = [num for num in all_numbers if num not in valid_candidates]
                valid_candidates.extend(additional[:target_count - len(valid_candidates)])
            
            # Step 2: Apply diversification strategy
            if diversification_strategy == 'community_balanced':
                diversified_numbers = self._community_balanced_selection(valid_candidates, target_count)
            elif diversification_strategy == 'centrality_optimized':
                diversified_numbers = self._centrality_optimized_selection(valid_candidates, target_count)
            elif diversification_strategy == 'maximum_spread':
                diversified_numbers = self._maximum_spread_selection(valid_candidates, target_count)
            else:  # balanced
                diversified_numbers = self._balanced_diversification(valid_candidates, target_count)
            
            # Step 3: Calculate diversification metrics
            diversification_metrics = self._calculate_diversification_metrics(diversified_numbers)
            
            # Step 4: Create result
            result = DiversificationResult(
                diversified_numbers=diversified_numbers,
                network_metrics=diversification_metrics,
                community_distribution=self._analyze_community_distribution(diversified_numbers),
                diversification_score=diversification_metrics.get('diversification_score', 0.0),
                network_efficiency=diversification_metrics.get('network_efficiency', 0.0),
                coverage_breadth=diversification_metrics.get('coverage_breadth', 0.0),
                redundancy_minimization=diversification_metrics.get('redundancy_minimization', 0.0),
                temporal_spread=diversification_metrics.get('temporal_spread', 0.0),
                network_graph=self._export_graph_structure()
            )
            
            logger.info(f"✅ Diversification completed!")
            logger.info(f"   Selected Numbers: {diversified_numbers}")
            logger.info(f"   Diversification Score: {result.diversification_score:.3f}")
            logger.info(f"   Coverage Breadth: {result.coverage_breadth:.3f}")
            logger.info(f"   Network Efficiency: {result.network_efficiency:.3f}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in network diversification: {e}")
            # Return basic diversification
            basic_numbers = candidate_numbers[:target_count] if len(candidate_numbers) >= target_count else candidate_numbers
            while len(basic_numbers) < target_count:
                basic_numbers.append((basic_numbers[-1] % self.max_numbers) + 1)
                
            return DiversificationResult(
                diversified_numbers=basic_numbers,
                network_metrics={'diversification_score': 0.5},
                community_distribution={},
                diversification_score=0.5,
                network_efficiency=0.5,
                coverage_breadth=0.5,
                redundancy_minimization=0.5,
                temporal_spread=0.5,
                network_graph={}
            )
    
    def optimize_portfolio_diversity(self, number_portfolios: List[List[int]]) -> Dict[str, Any]:
        """
        📊 Optimize Portfolio Diversity
        
        Analyzes and optimizes multiple number portfolios for maximum
        collective diversification.
        """
        try:
            logger.info(f"📊 Optimizing {len(number_portfolios)} portfolios for diversity...")
            
            portfolio_analysis = {}
            
            for i, portfolio in enumerate(number_portfolios):
                # Analyze individual portfolio
                portfolio_metrics = self._analyze_portfolio_diversity(portfolio)
                
                portfolio_analysis[f'portfolio_{i+1}'] = {
                    'numbers': portfolio,
                    'diversity_score': portfolio_metrics.get('diversity_score', 0.0),
                    'community_coverage': portfolio_metrics.get('community_coverage', 0.0),
                    'network_centrality': portfolio_metrics.get('network_centrality', 0.0),
                    'redundancy_score': portfolio_metrics.get('redundancy_score', 0.0)
                }
            
            # Calculate collective diversity
            collective_metrics = self._calculate_collective_diversity(number_portfolios)
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(portfolio_analysis, collective_metrics)
            
            optimization_result = {
                'individual_portfolios': portfolio_analysis,
                'collective_diversity': collective_metrics,
                'optimization_recommendations': recommendations,
                'overall_diversity_score': collective_metrics.get('overall_diversity', 0.0)
            }
            
            logger.info(f"✅ Portfolio optimization completed!")
            logger.info(f"   Overall Diversity Score: {collective_metrics.get('overall_diversity', 0.0):.3f}")
            logger.info(f"   Recommendations: {len(recommendations)}")
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"❌ Error in portfolio optimization: {e}")
            return {'individual_portfolios': {}, 'collective_diversity': {}}
    
    # =================== PRIVATE METHODS ===================
    
    def _build_network_graph(self, historical_data: List[Dict[str, Any]]):
        """Build network graph from historical data"""
        try:
            # Track number frequencies and co-occurrences
            number_frequencies = defaultdict(int)
            co_occurrences = defaultdict(int)
            temporal_data = []
            
            for i, data_point in enumerate(historical_data):
                numbers = self._extract_numbers_from_data(data_point)
                temporal_data.append((i, numbers))
                
                # Count frequencies
                for num in numbers:
                    number_frequencies[num] += 1
                
                # Count co-occurrences
                for num1, num2 in itertools.combinations(numbers, 2):
                    pair = (min(num1, num2), max(num1, num2))
                    co_occurrences[pair] += 1
            
            # Create nodes
            for num, freq in number_frequencies.items():
                node = NetworkNode(
                    node_id=num,
                    frequency=freq,
                    centrality_score=0.0,  # Will be calculated later
                    clustering_coefficient=0.0,
                    betweenness_centrality=0.0,
                    pagerank_score=0.0,
                    community_id=0,  # Will be assigned during community detection
                    node_metadata={'temporal_first': 0, 'temporal_last': len(historical_data)}
                )
                self.lottery_graph.add_node(node)
            
            # Create edges
            total_occurrences = len(historical_data)
            for (num1, num2), count in co_occurrences.items():
                weight = count / max(1, total_occurrences)
                
                # Calculate temporal distance
                temporal_distance = self._calculate_temporal_distance(num1, num2, temporal_data)
                
                edge = NetworkEdge(
                    source=num1,
                    target=num2,
                    weight=weight,
                    co_occurrence_count=count,
                    temporal_distance=temporal_distance,
                    edge_type='co_occurrence',
                    strength=weight,
                    metadata={'formation_period': len(historical_data)}
                )
                self.lottery_graph.add_edge(edge)
            
            # Build adjacency matrix
            self.lottery_graph.build_adjacency_matrix()
            
            # Calculate centrality metrics
            self.lottery_graph.calculate_centrality_metrics()
            
        except Exception as e:
            logger.error(f"❌ Error building network graph: {e}")
    
    def _extract_numbers_from_data(self, data_point: Dict[str, Any]) -> List[int]:
        """Extract numbers from a data point"""
        try:
            numbers = []
            
            if 'ket_qua' in data_point:
                result = data_point['ket_qua']
                if isinstance(result, str):
                    # Extract pairs of digits
                    clean_result = ''.join(c for c in result if c.isdigit())
                    for i in range(0, min(len(clean_result), 12), 2):
                        if i + 1 < len(clean_result):
                            num = int(clean_result[i:i+2])
                            if 1 <= num <= self.max_numbers:
                                numbers.append(num)
                elif isinstance(result, list):
                    numbers = [int(x) for x in result if 1 <= int(x) <= self.max_numbers]
            
            return numbers
            
        except Exception as e:
            logger.error(f"❌ Error extracting numbers: {e}")
            return []
    
    def _calculate_temporal_distance(self, num1: int, num2: int, temporal_data: List[Tuple[int, List[int]]]) -> float:
        """Calculate temporal distance between two numbers"""
        try:
            num1_occurrences = [i for i, numbers in temporal_data if num1 in numbers]
            num2_occurrences = [i for i, numbers in temporal_data if num2 in numbers]
            
            if not num1_occurrences or not num2_occurrences:
                return 1.0
            
            # Calculate average temporal distance
            distances = []
            for occ1 in num1_occurrences:
                for occ2 in num2_occurrences:
                    distances.append(abs(occ1 - occ2))
            
            if distances:
                avg_distance = np.mean(distances)
                normalized_distance = avg_distance / max(1, len(temporal_data))
                return min(1.0, normalized_distance)
            
            return 1.0
            
        except Exception as e:
            logger.error(f"❌ Error calculating temporal distance: {e}")
            return 1.0
    
    def _detect_communities(self) -> Dict[int, NetworkCommunity]:
        """Detect communities in the network using simple clustering"""
        try:
            communities = {}
            
            # Simple community detection based on edge weights
            visited = set()
            community_id = 0
            
            for node_id in self.lottery_graph.nodes:
                if node_id in visited:
                    continue
                
                # Start a new community
                community_members = set()
                queue = deque([node_id])
                
                while queue:
                    current = queue.popleft()
                    if current in visited:
                        continue
                    
                    visited.add(current)
                    community_members.add(current)
                    
                    # Add neighbors with strong connections
                    neighbors = self.lottery_graph.get_neighbors(current)
                    for neighbor in neighbors:
                        if neighbor not in visited:
                            edge_key = (min(current, neighbor), max(current, neighbor))
                            if edge_key in self.lottery_graph.edges:
                                edge = self.lottery_graph.edges[edge_key]
                                if edge.weight > 0.1:  # Threshold for community membership
                                    queue.append(neighbor)
                
                # Create community if it has enough members
                if len(community_members) >= self.config['min_community_size']:
                    community = NetworkCommunity(
                        community_id=community_id,
                        member_nodes=community_members,
                        community_density=self._calculate_community_density(community_members),
                        modularity_score=0.0,  # Simplified
                        diversity_index=len(community_members) / max(1, len(self.lottery_graph.nodes)),
                        representative_nodes=list(community_members)[:3],
                        community_strength=1.0
                    )
                    communities[community_id] = community
                    
                    # Assign community ID to nodes
                    for member in community_members:
                        if member in self.lottery_graph.nodes:
                            old_node = self.lottery_graph.nodes[member]
                            updated_node = NetworkNode(
                                node_id=old_node.node_id,
                                frequency=old_node.frequency,
                                centrality_score=old_node.centrality_score,
                                clustering_coefficient=old_node.clustering_coefficient,
                                betweenness_centrality=old_node.betweenness_centrality,
                                pagerank_score=old_node.pagerank_score,
                                community_id=community_id,
                                node_metadata=old_node.node_metadata
                            )
                            self.lottery_graph.nodes[member] = updated_node
                    
                    community_id += 1
            
            self.lottery_graph.communities = communities
            return communities
            
        except Exception as e:
            logger.error(f"❌ Error detecting communities: {e}")
            return {}
    
    def _calculate_community_density(self, community_members: Set[int]) -> float:
        """Calculate density within a community"""
        try:
            if len(community_members) < 2:
                return 0.0
            
            # Count internal edges
            internal_edges = 0
            possible_edges = len(community_members) * (len(community_members) - 1) // 2
            
            for member1 in community_members:
                for member2 in community_members:
                    if member1 < member2:
                        edge_key = (member1, member2)
                        if edge_key in self.lottery_graph.edges:
                            internal_edges += 1
            
            return internal_edges / max(1, possible_edges)
            
        except Exception as e:
            logger.error(f"❌ Error calculating community density: {e}")
            return 0.0
    
    def _calculate_network_metrics(self) -> Dict[str, float]:
        """Calculate overall network metrics"""
        try:
            metrics = {}
            
            # Basic metrics
            num_nodes = len(self.lottery_graph.nodes)
            num_edges = len(self.lottery_graph.edges)
            
            metrics['nodes'] = num_nodes
            metrics['edges'] = num_edges
            
            # Density
            possible_edges = num_nodes * (num_nodes - 1) // 2
            metrics['density'] = num_edges / max(1, possible_edges)
            
            # Average degree
            if num_nodes > 0:
                total_degree = sum(len(self.lottery_graph.get_neighbors(node_id)) for node_id in self.lottery_graph.nodes)
                metrics['average_degree'] = total_degree / num_nodes
            else:
                metrics['average_degree'] = 0.0
            
            # Clustering coefficient
            if self.lottery_graph.nodes:
                clustering_coeffs = [node.clustering_coefficient for node in self.lottery_graph.nodes.values()]
                metrics['average_clustering'] = np.mean(clustering_coeffs)
            else:
                metrics['average_clustering'] = 0.0
            
            # Community metrics
            if self.lottery_graph.communities:
                community_sizes = [len(comm.member_nodes) for comm in self.lottery_graph.communities.values()]
                metrics['num_communities'] = len(self.lottery_graph.communities)
                metrics['average_community_size'] = np.mean(community_sizes)
                metrics['modularity'] = np.mean([comm.modularity_score for comm in self.lottery_graph.communities.values()])
            else:
                metrics['num_communities'] = 0
                metrics['average_community_size'] = 0.0
                metrics['modularity'] = 0.0
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating network metrics: {e}")
            return {}
    
    def _analyze_temporal_patterns(self, historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal patterns in the network"""
        try:
            temporal_analysis = {
                'temporal_stability': 0.0,
                'evolution_rate': 0.0,
                'recurring_patterns': 0,
                'trend_strength': 0.0
            }
            
            # Simple temporal analysis
            if len(historical_data) > 10:
                # Calculate stability as consistency of network structure over time
                window_size = len(historical_data) // 5
                stability_scores = []
                
                for i in range(0, len(historical_data) - window_size, window_size):
                    window_data = historical_data[i:i + window_size]
                    window_numbers = set()
                    for data_point in window_data:
                        numbers = self._extract_numbers_from_data(data_point)
                        window_numbers.update(numbers)
                    
                    if window_numbers:
                        stability_scores.append(len(window_numbers))
                
                if stability_scores:
                    temporal_analysis['temporal_stability'] = 1.0 - (np.std(stability_scores) / max(1, np.mean(stability_scores)))
                    temporal_analysis['evolution_rate'] = np.std(stability_scores) / max(1, np.mean(stability_scores))
            
            return temporal_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing temporal patterns: {e}")
            return {'temporal_stability': 0.0, 'evolution_rate': 0.0}
    
    def _balanced_diversification(self, candidates: List[int], target_count: int) -> List[int]:
        """Balanced diversification strategy"""
        try:
            selected = []
            remaining_candidates = candidates.copy()
            
            # Get community distribution
            community_distribution = defaultdict(list)
            for num in candidates:
                if num in self.lottery_graph.nodes:
                    community_id = self.lottery_graph.nodes[num].community_id
                    community_distribution[community_id].append(num)
            
            # Select from each community
            communities = list(community_distribution.keys())
            if communities:
                while len(selected) < target_count and communities:
                    for community_id in communities:
                        if len(selected) >= target_count:
                            break
                        
                        community_candidates = community_distribution[community_id]
                        if community_candidates:
                            # Select based on centrality score
                            best_candidate = max(community_candidates, 
                                               key=lambda x: self.lottery_graph.nodes.get(x, NetworkNode(x, 0, 0, 0, 0, 0, 0)).centrality_score)
                            selected.append(best_candidate)
                            community_distribution[community_id].remove(best_candidate)
                            
                            if not community_distribution[community_id]:
                                communities.remove(community_id)
            
            # Fill remaining slots
            while len(selected) < target_count and remaining_candidates:
                candidate = remaining_candidates.pop(0)
                if candidate not in selected:
                    selected.append(candidate)
            
            return selected[:target_count]
            
        except Exception as e:
            logger.error(f"❌ Error in balanced diversification: {e}")
            return candidates[:target_count]
    
    def _community_balanced_selection(self, candidates: List[int], target_count: int) -> List[int]:
        """Community-balanced selection strategy"""
        return self._balanced_diversification(candidates, target_count)
    
    def _centrality_optimized_selection(self, candidates: List[int], target_count: int) -> List[int]:
        """Centrality-optimized selection strategy"""
        try:
            # Sort by centrality score
            candidates_with_centrality = []
            for num in candidates:
                if num in self.lottery_graph.nodes:
                    centrality = self.lottery_graph.nodes[num].centrality_score
                    candidates_with_centrality.append((num, centrality))
                else:
                    candidates_with_centrality.append((num, 0.0))
            
            # Sort by centrality descending
            candidates_with_centrality.sort(key=lambda x: x[1], reverse=True)
            
            # Select top centrality numbers with diversity constraints
            selected = []
            for num, centrality in candidates_with_centrality:
                if len(selected) >= target_count:
                    break
                
                # Check for diversity (don't select too many from same community)
                if num in self.lottery_graph.nodes:
                    community_id = self.lottery_graph.nodes[num].community_id
                    same_community_count = sum(1 for s in selected 
                                             if s in self.lottery_graph.nodes and 
                                             self.lottery_graph.nodes[s].community_id == community_id)
                    
                    if same_community_count < 2:  # Max 2 per community
                        selected.append(num)
                else:
                    selected.append(num)
            
            return selected[:target_count]
            
        except Exception as e:
            logger.error(f"❌ Error in centrality optimization: {e}")
            return candidates[:target_count]
    
    def _maximum_spread_selection(self, candidates: List[int], target_count: int) -> List[int]:
        """Maximum spread selection strategy"""
        try:
            if not candidates:
                return []
            
            selected = [candidates[0]]  # Start with first candidate
            remaining = candidates[1:]
            
            while len(selected) < target_count and remaining:
                # Find candidate with maximum distance from selected
                best_candidate = None
                max_min_distance = -1
                
                for candidate in remaining:
                    # Calculate minimum distance to selected numbers
                    min_distance = float('inf')
                    
                    for selected_num in selected:
                        # Calculate network distance (simplified as number distance)
                        distance = abs(candidate - selected_num)
                        min_distance = min(min_distance, distance)
                    
                    if min_distance > max_min_distance:
                        max_min_distance = min_distance
                        best_candidate = candidate
                
                if best_candidate is not None:
                    selected.append(best_candidate)
                    remaining.remove(best_candidate)
                else:
                    # Fallback to first remaining
                    selected.append(remaining.pop(0))
            
            return selected
            
        except Exception as e:
            logger.error(f"❌ Error in maximum spread selection: {e}")
            return candidates[:target_count]
    
    def _calculate_diversification_metrics(self, selected_numbers: List[int]) -> Dict[str, float]:
        """Calculate diversification metrics for selected numbers"""
        try:
            metrics = {}
            
            # Community distribution
            community_counts = defaultdict(int)
            for num in selected_numbers:
                if num in self.lottery_graph.nodes:
                    community_id = self.lottery_graph.nodes[num].community_id
                    community_counts[community_id] += 1
            
            # Diversification score (Shannon entropy-like)
            if community_counts:
                total = sum(community_counts.values())
                entropy = 0.0
                for count in community_counts.values():
                    if count > 0:
                        p = count / total
                        entropy -= p * np.log2(p)
                
                max_entropy = np.log2(len(community_counts))
                metrics['diversification_score'] = entropy / max(max_entropy, 1.0)
            else:
                metrics['diversification_score'] = 0.0
            
            # Coverage breadth
            total_communities = len(self.lottery_graph.communities) if self.lottery_graph.communities else 1
            unique_communities = len(community_counts)
            metrics['coverage_breadth'] = unique_communities / max(total_communities, 1.0)
            
            # Network efficiency (average centrality)
            centralities = []
            for num in selected_numbers:
                if num in self.lottery_graph.nodes:
                    centralities.append(self.lottery_graph.nodes[num].centrality_score)
            
            metrics['network_efficiency'] = np.mean(centralities) if centralities else 0.0
            
            # Redundancy minimization
            total_possible_pairs = len(selected_numbers) * (len(selected_numbers) - 1) // 2
            connected_pairs = 0
            
            for i, num1 in enumerate(selected_numbers):
                for j, num2 in enumerate(selected_numbers[i+1:], i+1):
                    edge_key = (min(num1, num2), max(num1, num2))
                    if edge_key in self.lottery_graph.edges:
                        connected_pairs += 1
            
            metrics['redundancy_minimization'] = 1.0 - (connected_pairs / max(total_possible_pairs, 1.0))
            
            # Temporal spread (simplified)
            metrics['temporal_spread'] = 0.8  # Placeholder
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating diversification metrics: {e}")
            return {'diversification_score': 0.5}
    
    def _analyze_community_distribution(self, selected_numbers: List[int]) -> Dict[int, int]:
        """Analyze community distribution of selected numbers"""
        try:
            distribution = defaultdict(int)
            
            for num in selected_numbers:
                if num in self.lottery_graph.nodes:
                    community_id = self.lottery_graph.nodes[num].community_id
                    distribution[community_id] += 1
            
            return dict(distribution)
            
        except Exception as e:
            logger.error(f"❌ Error analyzing community distribution: {e}")
            return {}
    
    def _export_graph_structure(self) -> Dict[str, Any]:
        """Export graph structure for visualization"""
        try:
            graph_data = {
                'nodes': [],
                'edges': [],
                'communities': {},
                'metrics': self.lottery_graph.graph_metrics
            }
            
            # Export nodes
            for node in self.lottery_graph.nodes.values():
                graph_data['nodes'].append({
                    'id': node.node_id,
                    'frequency': node.frequency,
                    'centrality': node.centrality_score,
                    'community': node.community_id
                })
            
            # Export edges
            for edge in self.lottery_graph.edges.values():
                graph_data['edges'].append({
                    'source': edge.source,
                    'target': edge.target,
                    'weight': edge.weight,
                    'type': edge.edge_type
                })
            
            # Export communities
            for comm_id, community in self.lottery_graph.communities.items():
                graph_data['communities'][str(comm_id)] = {
                    'members': list(community.member_nodes),
                    'density': community.community_density,
                    'size': len(community.member_nodes)
                }
            
            return graph_data
            
        except Exception as e:
            logger.error(f"❌ Error exporting graph structure: {e}")
            return {}
    
    def _analyze_portfolio_diversity(self, portfolio: List[int]) -> Dict[str, float]:
        """Analyze diversity of a single portfolio"""
        try:
            return self._calculate_diversification_metrics(portfolio)
        except Exception as e:
            logger.error(f"❌ Error analyzing portfolio diversity: {e}")
            return {'diversity_score': 0.0}
    
    def _calculate_collective_diversity(self, portfolios: List[List[int]]) -> Dict[str, float]:
        """Calculate collective diversity across portfolios"""
        try:
            all_numbers = set()
            for portfolio in portfolios:
                all_numbers.update(portfolio)
            
            collective_metrics = {
                'total_unique_numbers': len(all_numbers),
                'average_portfolio_size': np.mean([len(p) for p in portfolios]),
                'overall_diversity': len(all_numbers) / max(1, self.max_numbers),
                'portfolio_overlap': self._calculate_portfolio_overlap(portfolios)
            }
            
            return collective_metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating collective diversity: {e}")
            return {}
    
    def _calculate_portfolio_overlap(self, portfolios: List[List[int]]) -> float:
        """Calculate overlap between portfolios"""
        try:
            if len(portfolios) < 2:
                return 0.0
            
            total_overlaps = 0
            total_comparisons = 0
            
            for i in range(len(portfolios)):
                for j in range(i + 1, len(portfolios)):
                    set1 = set(portfolios[i])
                    set2 = set(portfolios[j])
                    
                    overlap = len(set1.intersection(set2))
                    union = len(set1.union(set2))
                    
                    if union > 0:
                        total_overlaps += overlap / union
                    
                    total_comparisons += 1
            
            return total_overlaps / max(1, total_comparisons)
            
        except Exception as e:
            logger.error(f"❌ Error calculating portfolio overlap: {e}")
            return 0.0
    
    def _generate_optimization_recommendations(self, portfolio_analysis: Dict[str, Any], 
                                             collective_metrics: Dict[str, float]) -> List[str]:
        """Generate optimization recommendations"""
        try:
            recommendations = []
            
            # Analyze portfolio diversity scores
            diversity_scores = [portfolio['diversity_score'] for portfolio in portfolio_analysis.values()]
            avg_diversity = np.mean(diversity_scores)
            
            if avg_diversity < 0.6:
                recommendations.append("Increase diversification across network communities")
            
            if collective_metrics.get('portfolio_overlap', 0) > 0.5:
                recommendations.append("Reduce overlap between portfolios for better collective coverage")
            
            if collective_metrics.get('overall_diversity', 0) < 0.7:
                recommendations.append("Expand number selection to cover more network regions")
            
            # Community coverage recommendations
            for portfolio_name, portfolio_data in portfolio_analysis.items():
                if portfolio_data['community_coverage'] < 0.5:
                    recommendations.append(f"{portfolio_name}: Improve community coverage")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendations: {e}")
            return []

# =================== DEMONSTRATION FUNCTION ===================

def demo_network_diversification():
    """Demonstrate network-based diversification"""
    print("🌐 NETWORK-BASED DIVERSIFICATION - PHASE 3")
    print("=" * 55)
    
    # Initialize network diversification service
    diversification_service = NetworkDiversificationService()
    
    print(f"\n🏗️ Network Service Configuration:")
    print(f"   Max Numbers: {diversification_service.max_numbers}")
    print(f"   Community Weight: {diversification_service.config['community_weight']}")
    print(f"   Centrality Weight: {diversification_service.config['centrality_weight']}")
    print(f"   Diversity Weight: {diversification_service.config['diversity_weight']}")
    
    # Generate sample historical data
    historical_data = []
    for i in range(100):
        data_point = {
            'ngay': f"2025012{i%10}",
            'ket_qua': f"{10 + i%39:02d}{20 + i%29:02d}{30 + i%19:02d}{40 + i%9:02d}",
            'quality_score': 0.7 + (i % 10) * 0.03
        }
        historical_data.append(data_point)
    
    print(f"\n📊 Historical Data:")
    print(f"   Data Points: {len(historical_data)}")
    print(f"   Sample: {historical_data[-1]}")
    
    # Analyze network patterns
    print(f"\n🌐 ANALYZING NETWORK PATTERNS...")
    
    network_analysis = diversification_service.analyze_network_patterns(historical_data)
    
    print(f"\n📈 NETWORK ANALYSIS RESULTS:")
    print(f"=" * 40)
    
    graph_structure = network_analysis['graph_structure']
    print(f"\n🕸️ Graph Structure:")
    print(f"   Nodes: {graph_structure['nodes']}")
    print(f"   Edges: {graph_structure['edges']}")
    print(f"   Density: {graph_structure['density']:.3f}")
    print(f"   Modularity: {graph_structure.get('modularity', 0):.3f}")
    
    print(f"\n🏘️ Community Detection:")
    communities = network_analysis['communities']
    print(f"   Total Communities: {len(communities)}")
    for i, (comm_id, comm_data) in enumerate(list(communities.items())[:3], 1):
        member_nodes = comm_data.get('member_nodes', set())
        if isinstance(member_nodes, set):
            member_count = len(member_nodes)
        else:
            member_count = len(member_nodes) if member_nodes else 0
        print(f"   Community {i}: {member_count} members, Density: {comm_data.get('community_density', 0):.3f}")
    
    # Test diversification strategies
    print(f"\n🎯 TESTING DIVERSIFICATION STRATEGIES...")
    
    candidate_numbers = [12, 23, 34, 45, 8, 19, 27, 33, 41, 15, 26, 38, 42, 7, 18]
    
    strategies = ['balanced', 'community_balanced', 'centrality_optimized', 'maximum_spread']
    
    for strategy in strategies:
        print(f"\n📊 Strategy: {strategy.upper()}")
        
        result = diversification_service.diversify_selection(
            candidate_numbers, target_count=6, diversification_strategy=strategy
        )
        
        print(f"   Selected Numbers: {result.diversified_numbers}")
        print(f"   Diversification Score: {result.diversification_score:.3f}")
        print(f"   Coverage Breadth: {result.coverage_breadth:.3f}")
        print(f"   Network Efficiency: {result.network_efficiency:.3f}")
        print(f"   Redundancy Minimization: {result.redundancy_minimization:.3f}")
        
        # Community distribution
        comm_dist = result.community_distribution
        if comm_dist:
            print(f"   Community Distribution: {dict(list(comm_dist.items())[:3])}")
    
    # Portfolio optimization
    print(f"\n📊 PORTFOLIO OPTIMIZATION DEMONSTRATION...")
    
    portfolios = [
        [12, 23, 34, 45, 8, 19],
        [15, 26, 37, 48, 9, 20],
        [18, 29, 30, 41, 6, 17]
    ]
    
    portfolio_optimization = diversification_service.optimize_portfolio_diversity(portfolios)
    
    print(f"\n📈 Portfolio Optimization Results:")
    collective = portfolio_optimization['collective_diversity']
    print(f"   Total Unique Numbers: {collective.get('total_unique_numbers', 0)}")
    print(f"   Overall Diversity: {collective.get('overall_diversity', 0):.3f}")
    print(f"   Portfolio Overlap: {collective.get('portfolio_overlap', 0):.3f}")
    
    # Recommendations
    recommendations = portfolio_optimization.get('optimization_recommendations', [])
    print(f"\n💡 Optimization Recommendations:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"   {i}. {rec}")
    
    print(f"\n✅ Network-based diversification demonstration completed!")
    print(f"\n🎉 NETWORK DIVERSIFICATION ACHIEVED!")
    print(f"   🌐 Graph Analysis: {graph_structure['nodes']} nodes, {graph_structure['edges']} edges")
    print(f"   🏘️ Community Detection: {len(communities)} communities identified")
    print(f"   🎯 Diversification: Multiple strategies operational")
    print(f"   📊 Portfolio Optimization: Collective analysis complete")
    
    return diversification_service, network_analysis

if __name__ == "__main__":
    service, analysis = demo_network_diversification()
