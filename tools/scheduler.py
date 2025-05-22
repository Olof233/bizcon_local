"""
Scheduler tool for bizCon framework.
"""
from typing import Dict, List, Any, Optional
import json
import os
import random
import datetime

from .base import BusinessTool


class SchedulerTool(BusinessTool):
    """
    Scheduler tool for finding availability and booking appointments.
    """
    
    def __init__(self, error_rate: float = 0.05):
        """
        Initialize the scheduler tool.
        
        Args:
            error_rate: Probability of simulating a tool error (0-1)
        """
        super().__init__(
            tool_id="scheduler",
            name="Appointment Scheduler",
            description="Check availability and schedule appointments with sales representatives, technical specialists, or support staff",
            parameters={
                "meeting_type": {
                    "type": "string",
                    "description": "Type of meeting to schedule (e.g., 'sales_call', 'product_demo', 'technical_consultation', 'support_session')",
                    "required": True
                },
                "date": {
                    "type": "string",
                    "description": "Preferred date (YYYY-MM-DD format)",
                    "required": False
                },
                "time_range": {
                    "type": "string",
                    "description": "Preferred time range (e.g., '09:00-17:00')",
                    "required": False
                },
                "duration": {
                    "type": "integer",
                    "description": "Duration in minutes (default is 60)",
                    "required": False
                },
                "participants": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Types of staff needed (e.g., ['sales_rep', 'technical_specialist'])",
                    "required": False
                },
                "product_id": {
                    "type": "string",
                    "description": "Product ID if this is a product-specific meeting",
                    "required": False
                },
                "industry": {
                    "type": "string",
                    "description": "Customer industry for specialist assignment",
                    "required": False
                },
                "timezone": {
                    "type": "string",
                    "description": "Customer timezone (default is 'America/New_York')",
                    "required": False
                },
                "book": {
                    "type": "boolean",
                    "description": "Whether to book the first available slot (default is false, just check availability)",
                    "required": False
                }
            },
            error_rate=error_rate
        )
    
    def _execute(self, parameters: Dict[str, Any]) -> Any:
        """
        Execute the scheduling request.
        
        Args:
            parameters: Dictionary with parameters
                - meeting_type: Type of meeting to schedule
                - date: Preferred date
                - time_range: Preferred time range
                - duration: Duration in minutes
                - participants: Types of staff needed
                - product_id: Product ID for product-specific meetings
                - industry: Customer industry
                - timezone: Customer timezone
                - book: Whether to book the first available slot
        
        Returns:
            Available time slots or booking confirmation
        """
        meeting_type = parameters.get("meeting_type")
        date_str = parameters.get("date")
        time_range = parameters.get("time_range", "09:00-17:00")
        duration = parameters.get("duration", 60)
        participants = parameters.get("participants", [])
        product_id = parameters.get("product_id")
        industry = parameters.get("industry")
        timezone = parameters.get("timezone", "America/New_York")
        book = parameters.get("book", False)
        
        # If no date is provided, use the next business day
        if not date_str:
            now = datetime.datetime.now()
            next_day = now + datetime.timedelta(days=1)
            # Skip to Monday if it's Friday
            if next_day.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
                days_to_add = 7 - next_day.weekday() + 1  # Add days to reach Monday
                next_day = now + datetime.timedelta(days=days_to_add)
            date_str = next_day.strftime("%Y-%m-%d")
        
        # Parse time range
        try:
            start_time_str, end_time_str = time_range.split("-")
            start_hour, start_minute = map(int, start_time_str.split(":"))
            end_hour, end_minute = map(int, end_time_str.split(":"))
        except (ValueError, AttributeError):
            return {"error": f"Invalid time range format: {time_range}. Use format '09:00-17:00'"}
        
        # Generate available time slots
        available_slots = self._generate_available_slots(
            date_str, start_hour, start_minute, end_hour, end_minute, duration
        )
        
        # Filter slots based on participant availability
        if participants:
            available_slots = self._filter_by_participants(
                available_slots, participants, product_id, industry
            )
        
        # If no slots are available, suggest alternative dates
        if not available_slots:
            return self._suggest_alternative_dates(
                date_str, participants, product_id, industry
            )
        
        # If booking is requested, book the first available slot
        if book and available_slots:
            booked_slot = available_slots[0]
            confirmation_id = f"CONF-{random.randint(100000, 999999)}"
            
            return {
                "status": "confirmed",
                "confirmation_id": confirmation_id,
                "meeting_type": meeting_type,
                "date": date_str,
                "start_time": booked_slot["start_time"],
                "end_time": booked_slot["end_time"],
                "duration": duration,
                "participants": self._assign_specific_participants(participants, product_id, industry),
                "timezone": timezone,
                "product_id": product_id,
                "location": "Virtual (link will be sent via email)",
                "notes": "You will receive a calendar invitation and confirmation email shortly."
            }
        
        # Otherwise, just return available slots
        return {
            "date": date_str,
            "timezone": timezone,
            "available_slots": available_slots,
            "message": f"{len(available_slots)} time slots available on {date_str}",
            "booking_instructions": "To book a slot, call this tool again with the same parameters plus 'book: true'"
        }
    
    def _generate_available_slots(self, 
                                 date_str: str, 
                                 start_hour: int, 
                                 start_minute: int, 
                                 end_hour: int, 
                                 end_minute: int, 
                                 duration: int) -> List[Dict[str, str]]:
        """
        Generate available time slots for the given parameters.
        
        Args:
            date_str: Date string in YYYY-MM-DD format
            start_hour: Start hour
            start_minute: Start minute
            end_hour: End hour
            end_minute: End minute
            duration: Duration in minutes
            
        Returns:
            List of available time slots
        """
        # Parse date
        try:
            year, month, day = map(int, date_str.split("-"))
            date = datetime.date(year, month, day)
        except ValueError:
            return []
        
        # Don't schedule on weekends
        if date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return []
        
        # Generate time slots
        slots = []
        current_time = datetime.datetime.combine(
            date, datetime.time(start_hour, start_minute)
        )
        end_time = datetime.datetime.combine(
            date, datetime.time(end_hour, end_minute)
        )
        
        while current_time + datetime.timedelta(minutes=duration) <= end_time:
            # Add some randomness to availability
            if random.random() > 0.3:  # 70% chance a slot is available
                slot_end = current_time + datetime.timedelta(minutes=duration)
                slots.append({
                    "start_time": current_time.strftime("%H:%M"),
                    "end_time": slot_end.strftime("%H:%M")
                })
            
            # Move to next slot (30-minute intervals)
            current_time += datetime.timedelta(minutes=30)
        
        return slots
    
    def _filter_by_participants(self, 
                               slots: List[Dict[str, str]], 
                               participants: List[str],
                               product_id: Optional[str],
                               industry: Optional[str]) -> List[Dict[str, str]]:
        """
        Filter slots based on participant availability.
        
        Args:
            slots: List of time slots
            participants: Required participant types
            product_id: Product ID
            industry: Industry
            
        Returns:
            Filtered list of time slots
        """
        # Simulate reduced availability based on participant requirements
        if not participants:
            return slots
        
        # More participants = fewer available slots
        availability_factor = 0.9 ** len(participants)
        
        # Industry and product specificity further reduces availability
        if industry:
            availability_factor *= 0.9
        
        if product_id:
            availability_factor *= 0.8
        
        # Filter slots
        filtered_slots = []
        for slot in slots:
            if random.random() < availability_factor:
                filtered_slots.append(slot)
        
        return filtered_slots
    
    def _assign_specific_participants(self, 
                                     participant_types: List[str],
                                     product_id: Optional[str],
                                     industry: Optional[str]) -> List[Dict[str, str]]:
        """
        Assign specific participants based on requirements.
        
        Args:
            participant_types: Required participant types
            product_id: Product ID
            industry: Industry
            
        Returns:
            List of assigned participants
        """
        # Mock participant database
        sales_reps = [
            {"id": "SR001", "name": "Emma Johnson", "specialties": ["financial_services", "healthcare"]},
            {"id": "SR002", "name": "Michael Chen", "specialties": ["retail", "manufacturing"]},
            {"id": "SR003", "name": "Sophia Rodriguez", "specialties": ["telecommunications", "technology"]}
        ]
        
        technical_specialists = [
            {"id": "TS001", "name": "David Kim", "specialties": ["data_analytics", "cloud_services"]},
            {"id": "TS002", "name": "Olivia Patel", "specialties": ["data_management", "security"]},
            {"id": "TS003", "name": "James Wilson", "specialties": ["implementation", "integrations"]}
        ]
        
        support_specialists = [
            {"id": "SS001", "name": "Sarah Thompson", "specialties": ["user_training", "troubleshooting"]},
            {"id": "SS002", "name": "Robert Lee", "specialties": ["configuration", "customization"]}
        ]
        
        # Map participant types to databases
        participant_db = {
            "sales_rep": sales_reps,
            "technical_specialist": technical_specialists,
            "support_specialist": support_specialists
        }
        
        # Assign participants
        assigned = []
        for participant_type in participant_types:
            if participant_type in participant_db:
                candidates = participant_db[participant_type]
                
                # Filter by industry if specified
                if industry:
                    industry_candidates = [c for c in candidates if industry in c.get("specialties", [])]
                    if industry_candidates:
                        candidates = industry_candidates
                
                # Filter by product if specified
                if product_id and participant_type == "technical_specialist":
                    product_type = product_id.split("_")[0] if "_" in product_id else product_id
                    product_candidates = [c for c in candidates if product_type in c.get("specialties", [])]
                    if product_candidates:
                        candidates = product_candidates
                
                # Select a random candidate
                if candidates:
                    selected = random.choice(candidates)
                    assigned.append({
                        "type": participant_type,
                        "id": selected["id"],
                        "name": selected["name"]
                    })
        
        return assigned
    
    def _suggest_alternative_dates(self, 
                                  date_str: str, 
                                  participants: List[str],
                                  product_id: Optional[str],
                                  industry: Optional[str]) -> Dict[str, Any]:
        """
        Suggest alternative dates when no slots are available.
        
        Args:
            date_str: Requested date
            participants: Required participant types
            product_id: Product ID
            industry: Industry
            
        Returns:
            Alternative date suggestions
        """
        try:
            year, month, day = map(int, date_str.split("-"))
            requested_date = datetime.date(year, month, day)
        except ValueError:
            # Fallback to current date if invalid date
            requested_date = datetime.date.today()
        
        # Generate alternative dates (next 5 business days)
        alternatives = []
        current_date = requested_date + datetime.timedelta(days=1)
        
        while len(alternatives) < 3:
            # Skip weekends
            if current_date.weekday() < 5:  # 0-4 are weekdays
                # Generate slots for this date
                slots = self._generate_available_slots(
                    current_date.strftime("%Y-%m-%d"),
                    9, 0, 17, 0, 60
                )
                
                # Filter by participants
                slots = self._filter_by_participants(slots, participants, product_id, industry)
                
                if slots:
                    alternatives.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "available_slots": slots
                    })
            
            current_date += datetime.timedelta(days=1)
        
        return {
            "status": "no_availability",
            "requested_date": date_str,
            "message": f"No availability on {date_str} with the requested criteria",
            "alternatives": alternatives
        }