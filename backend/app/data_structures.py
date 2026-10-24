"""
================================================================================
FoodShare – Data Structures & Algorithms Core Engine
Implementation of foundational computer science principles:
1. FIFO Queue (collections.deque): Pending pickup and delivery assignments.
2. Min-Heap Priority Queue (heapq): Expiry prioritization for near-spoilage meals.
3. Inverted Index Hash Map (dict): O(1) keyword indexing for Chatbot Assistant.
4. City Logistics Graph (Adjacency List + Dijkstra): Shortest transit path routing.
================================================================================
"""

from collections import deque
import heapq
import re
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

# ==============================================================================
# 1. FIFO TASK QUEUE (collections.deque)
# Used for volunteer pickup dispatch to ensure first-claimed donations get assigned first.
# Time Complexity: O(1) amortized enqueue (append) and O(1) dequeue (popleft).
# ==============================================================================
class TaskFIFOQueue:
    def __init__(self):
        self._queue: deque = deque()

    def enqueue(self, task: Dict[str, Any]) -> None:
        """Add a newly created delivery task to the tail of the queue."""
        self._queue.append(task)

    def dequeue(self) -> Optional[Dict[str, Any]]:
        """Extract the earliest pending delivery task from the head in O(1) time."""
        if not self._queue:
            return None
        return self._queue.popleft()

    def peek(self) -> Optional[Dict[str, Any]]:
        """Inspect the head task without removing it."""
        return self._queue[0] if self._queue else None

    def size(self) -> int:
        return len(self._queue)

    def to_list(self) -> List[Dict[str, Any]]:
        return list(self._queue)


# ==============================================================================
# 2. PRIORITY QUEUE / MIN-HEAP (heapq)
# Used to auto-prioritize perishable food items approaching safe consumption deadline.
# Invariant: Root element always has minimum expiry timestamp (highest urgency).
# Time Complexity: O(log N) insertion, O(log N) pop, O(1) peek.
# ==============================================================================
class FoodExpiryPriorityQueue:
    def __init__(self):
        self._heap: List[Tuple[float, int, Dict[str, Any]]] = []

    def push(self, donation: Dict[str, Any]) -> None:
        """
        Inserts donation into min-heap prioritized by epoch expiry timestamp.
        Tuple structure: (expiry_timestamp, donation_id, donation_payload)
        """
        expiry_ts = donation.get("expiry_timestamp", 0.0)
        donation_id = donation.get("id", 0)
        heapq.heappush(self._heap, (expiry_ts, donation_id, donation))

    def pop_most_urgent(self) -> Optional[Dict[str, Any]]:
        """Extracts the most urgently expiring food donation in O(log N) time."""
        if not self._heap:
            return None
        _, _, donation = heapq.heappop(self._heap)
        return donation

    def peek_most_urgent(self) -> Optional[Dict[str, Any]]:
        """Returns the root urgent item in O(1) without popping."""
        if not self._heap:
            return None
        return self._heap[0][2]

    def size(self) -> int:
        return len(self._heap)

    def to_sorted_list(self) -> List[Dict[str, Any]]:
        """Returns all items sorted from earliest to latest expiry."""
        copied = list(self._heap)
        sorted_items = []
        while copied:
            sorted_items.append(heapq.heappop(copied)[2])
        return sorted_items


# ==============================================================================
# 3. INVERTED INDEX HASH MAP (dict)
# Used for instant FAQ chatbot question resolution without full database scans.
# Maps tokenized words to sets of FAQ intent IDs with relevance scoring.
# Time Complexity: O(1) average hash lookup per token.
# ==============================================================================
class FAQInvertedIndex:
    def __init__(self):
        self.kb: Dict[str, Dict[str, Any]] = {
            "register_login": {
                "keywords": ["register", "signup", "login", "signin", "account", "password", "portal"],
                "reply": "To register: Click 'Register' in the top navigation bar, choose your role (Donor, NGO, or Volunteer), and enter your contact details. NGOs must provide their registration number. To log in: Click 'Sign In' and enter your email and password, or use the demo quick-fill buttons."
            },
            "donate_food": {
                "keywords": ["donate", "food", "surplus", "list", "post", "meals", "produce", "bakery"],
                "reply": "To donate surplus food: 1. Sign in as a Donor. 2. Go to the Donor Dashboard or click 'Donate Food'. 3. Fill in the food name, category, quantity, dietary classification, prep time, safe expiry deadline, and pickup address. 4. Click 'Publish Donation to Pool'. Verified NGOs will immediately be able to discover and claim it!"
            },
            "schedule_pickup": {
                "keywords": ["schedule", "pickup", "collection", "window", "gate", "packaging", "thermal"],
                "reply": "To schedule a pickup: 1. Open the 'Logistics' page and switch to Donor Logistics. 2. Select your listed donation from the dropdown. 3. Choose your pickup date, time, and window (Morning, Afternoon, Evening, or Night). 4. Select packaging (e.g., Hot Insulated Crates) and gate contact. 5. Click 'Confirm Pickup Schedule'. An assigned volunteer is automatically linked!"
            },
            "ngo_claim": {
                "keywords": ["ngo", "claim", "request", "shelter", "charity", "beneficiaries"],
                "reply": "For NGOs: 1. Sign in with a verified NGO account. 2. Visit the 'Find Food' catalog or NGO Dashboard. 3. Filter donations by category (Cooked Meals, Bakery, Produce) or dietary preference. 4. Click 'Claim Food', specify the required quantity and distribution purpose, and submit. The system reserves the stock atomically and queues a volunteer delivery task."
            },
            "volunteer_tasks": {
                "keywords": ["volunteer", "deliver", "task", "pickup", "transit", "accept", "transport"],
                "reply": "For Volunteers: 1. Sign in as a Volunteer and go to the Volunteer Dashboard. 2. Browse available delivery assignments in the FIFO Queue. 3. Click 'Accept Delivery Task'. 4. Collect food from the donor and advance the status through each stage: Picked Up → In Transit → Delivered."
            },
            "delivery_tracking": {
                "keywords": ["track", "tracking", "status", "stage", "pipeline", "where", "location"],
                "reply": "To track delivery status: Open the 'Logistics' tab → NGO Logistics. Each claimed item displays a 5-step delivery pipeline: 1. Accepted → 2. Scheduled → 3. Picked Up → 4. In Transit → 5. Delivered. You can check the assigned volunteer's contact and confirm receipt once received."
            },
            "admin_inventory": {
                "keywords": ["admin", "inventory", "stock", "operations", "fleet", "audit", "negative"],
                "reply": "For Administrators: Open the Admin Dashboard or Logistics → Admin Logistics. You can oversee central inventory balances (Total Listed, Available, Reserved, Delivered), monitor near-expiry alerts (< 4h remaining), prevent negative stock, reassign volunteers, and inspect security audit logs."
            },
            "language_switch": {
                "keywords": ["language", "translate", "hindi", "marathi", "tamil", "telugu", "spanish", "arabic", "chinese", "russian"],
                "reply": "To change language: Select your preferred language from the dropdown in the top-right of the navigation bar. FoodShare supports 9 languages: English, Marathi, Hindi, Tamil, Telugu, Russian, Spanish, Arabic (with full Right-to-Left bidirectional layout), and Chinese."
            },
            "troubleshooting": {
                "keywords": ["fail", "error", "load", "stuck", "cannot", "issue", "problem", "bug"],
                "reply": "Troubleshooting guide: 1. Verify that all mandatory fields marked with an asterisk (*) are filled. 2. Ensure pickup dates and times are not set in the past. 3. Confirm you are signed in with the correct role (e.g., only Donors can publish food). 4. Refresh your browser page. If issues persist, email support@foodshare.org or call our helpline at +91 98220 12345."
            },
            "navigation_dashboard": {
                "keywords": ["navigate", "dashboard", "menu", "portal", "find", "where do i go"],
                "reply": "To navigate FoodShare: Use the top navigation bar to access Home, How It Works, About Us, Donate Food, Find Food, Volunteer, and Logistics. Once signed in, click your user badge in the header to open your role-specific dashboard (Donor, NGO, Volunteer, or Admin)."
            }
        }
        self.index: Dict[str, List[str]] = {}
        self._build_inverted_index()

    def _build_inverted_index(self):
        for intent_id, data in self.kb.items():
            for kw in data["keywords"]:
                word = kw.lower().strip()
                if word not in self.index:
                    self.index[word] = []
                self.index[word].append(intent_id)

    def query(self, text: str) -> Optional[str]:
        tokens = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        match_scores: Dict[str, int] = {}
        for token in tokens:
            if token in self.index:
                for intent_id in self.index[token]:
                    match_scores[intent_id] = match_scores.get(intent_id, 0) + 1
        
        if not match_scores:
            return None
        
        best_intent = max(match_scores, key=match_scores.get)
        return self.kb[best_intent]["reply"]


# ==============================================================================
# 4. CITY LOGISTICS GRAPH & DIJKSTRA'S SHORTEST PATH ROUTING
# Models urban pickup nodes, transit junctions, and destination NGO shelters.
# Time Complexity: O((V + E) log V) solved using min-heap priority queue.
# ==============================================================================
class LogisticsNetworkGraph:
    def __init__(self):
        # Adjacency list: node -> list of (neighbor, distance_in_km, travel_time_mins)
        self.adj_list: Dict[str, List[Tuple[str, float, float]]] = {}
        self._build_default_city_network()

    def add_edge(self, u: str, v: str, dist_km: float, time_mins: float, bidirectional: bool = True):
        if u not in self.adj_list:
            self.adj_list[u] = []
        if v not in self.adj_list:
            self.adj_list[v] = []
        self.adj_list[u].append((v, dist_km, time_mins))
        if bidirectional:
            self.adj_list[v].append((u, dist_km, time_mins))

    def _build_default_city_network(self):
        # Chhatrapati Sambhajinagar urban logistics topology
        self.add_edge("Green Bites Banquet (Cidco)", "Kranti Chowk Central Transit Hub", 3.2, 8.5)
        self.add_edge("Fresh Crust Bakery (Station Rd)", "Kranti Chowk Central Transit Hub", 2.1, 5.0)
        self.add_edge("Kranti Chowk Central Transit Hub", "Anna Seva Foundation (Samarth Nagar)", 1.8, 5.0)
        self.add_edge("Kranti Chowk Central Transit Hub", "Hope For All NGO (Shanti Nagar)", 2.3, 6.0)
        self.add_edge("Fresh Crust Bakery (Station Rd)", "Railway Station Shelter Home", 0.9, 2.5)
        self.add_edge("Green Bites Banquet (Cidco)", "Hope For All NGO (Shanti Nagar)", 4.1, 11.0)

    def dijkstra_shortest_path(self, start_node: str, end_node: str) -> Dict[str, Any]:
        """Calculates minimal travel time route between donor and shelter."""
        if start_node not in self.adj_list or end_node not in self.adj_list:
            return {"error": "Invalid origin or destination node"}

        # Min-Heap stores: (current_time, current_dist, current_node, path_history)
        pq = [(0.0, 0.0, start_node, [start_node])]
        visited = set()

        while pq:
            time_spent, dist_traveled, current, path = heapq.heappop(pq)

            if current == end_node:
                return {
                    "origin": start_node,
                    "destination": end_node,
                    "optimal_path": path,
                    "total_distance_km": round(dist_traveled, 2),
                    "estimated_time_mins": round(time_spent, 1),
                    "stops": len(path) - 1
                }

            if current in visited:
                continue
            visited.add(current)

            for neighbor, edge_dist, edge_time in self.adj_list.get(current, []):
                if neighbor not in visited:
                    heapq.heappush(pq, (
                        time_spent + edge_time,
                        dist_traveled + edge_dist,
                        neighbor,
                        path + [neighbor]
                    ))

        return {"error": "No route exists between the specified nodes"}
