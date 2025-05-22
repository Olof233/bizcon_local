"""
Service complaints business scenarios.
"""
from typing import Dict, List, Any, Optional
import json
import os

from .base import BusinessScenario


class HighValueCustomerComplaint(BusinessScenario):
    """
    High-value customer complaint scenario.
    
    Tests how well the model handles complex complaint resolution for a 
    high-value customer, requiring empathy, problem-solving, and business acumen.
    """
    
    def __init__(self, scenario_id: str = "complaint_001"):
        """
        Initialize the high-value customer complaint scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Enterprise Customer Service Failure",
            description="Resolving a complex service failure complaint from a major enterprise customer",
            industry="SaaS",
            complexity="complex",
            tools_required=["customer_history", "support_ticket", "order_management"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "I'm the CTO of TechGlobal, and I'm extremely disappointed with the service outage our team experienced yesterday. This is the third major disruption in two months, and it's affecting our business operations. We're paying for your highest enterprise tier specifically for the 99.99% uptime SLA, but we're not seeing that reliability. I need this escalated immediately.",
                "expected_tool_calls": [
                    {
                        "tool_id": "customer_history",
                        "parameters": {
                            "customer_name": "TechGlobal",
                            "account_type": "enterprise",
                            "lookup_fields": ["subscription_tier", "contract_details", "recent_incidents", "account_health"]
                        }
                    }
                ]
            },
            {
                "user_message": "Yes, we reported all of these outages. The incident numbers are INC-7723, INC-8015, and yesterday's was INC-8544. Each time, we've had teams of developers sitting idle, costing us thousands in lost productivity. Your support team has been responsive, but we keep getting different explanations for the root cause, and no clear indication that the underlying issues are being addressed systematically.",
                "expected_tool_calls": [
                    {
                        "tool_id": "support_ticket",
                        "parameters": {
                            "ticket_ids": ["INC-7723", "INC-8015", "INC-8544"],
                            "fields": ["status", "root_cause", "resolution", "impact", "next_steps"]
                        }
                    }
                ]
            },
            {
                "user_message": "I appreciate you compiling that information. According to our contract, we're eligible for service credits due to these outages, but that's not really what we're after. What we need is confidence that this won't happen again. Our annual renewal is coming up in two months, and frankly, we're evaluating other options. What concrete steps are you taking to prevent these issues, and what kind of compensation or accommodations can you offer for the business impact we've experienced?",
                "expected_tool_calls": [
                    {
                        "tool_id": "order_management",
                        "parameters": {
                            "customer_name": "TechGlobal",
                            "lookup_fields": ["contract_renewal_date", "service_credits_available", "account_executive", "upsell_opportunities", "retention_risk"]
                        }
                    }
                ]
            },
            {
                "user_message": "That sounds like a reasonable approach. I'd like to see the technical remediation plan in writing, and I want to be included in the weekly status updates on the implementation. Regarding the service credits and complimentary training, that would help demonstrate good faith. I'll also take you up on the executive briefing with your CTO. Let's schedule that for next week if possible, and we can reassess our position on the renewal after seeing some progress.",
                "expected_tool_calls": [
                    {
                        "tool_id": "support_ticket",
                        "parameters": {
                            "create_ticket": True,
                            "customer_name": "TechGlobal",
                            "issue_description": "High-priority account escalation: Service reliability concerns affecting renewal decision. Requires executive attention, technical remediation plan, and compensation discussion.",
                            "severity": "high",
                            "assignment_group": "executive_response_team",
                            "follow_up_required": True,
                            "follow_up_date": "2025-05-24"
                        }
                    }
                ]
            }
        ]
    
    def _initialize_ground_truth(self) -> Dict[str, Any]:
        """
        Initialize ground truth information.
        
        Returns:
            Dictionary with ground truth data
        """
        return {
            "customer_information": {
                "company_name": "TechGlobal, Inc.",
                "industry": "Financial Technology",
                "account_tier": "Enterprise Premium",
                "annual_contract_value": "$1.25M",
                "customer_since": "2023-04-15",
                "contract_renewal_date": "2025-07-31",
                "employees_using_platform": 2750,
                "strategic_value": "High - reference customer, industry influencer",
                "current_sentiment": "At risk - considering alternatives",
                "account_contacts": {
                    "primary_technical": {
                        "name": "Jordan Chen",
                        "title": "CTO",
                        "influence": "Final decision maker on renewal"
                    },
                    "primary_business": {
                        "name": "Morgan Reynolds",
                        "title": "COO",
                        "influence": "Key influencer, focused on operational impact"
                    },
                    "day_to_day": {
                        "name": "Taylor Washington",
                        "title": "VP of Engineering",
                        "influence": "Technical evaluator, manages relationship"
                    }
                }
            },
            "service_incidents": {
                "INC-7723": {
                    "date": "2025-03-18",
                    "duration": "3 hours 42 minutes",
                    "affected_services": ["API Gateway", "Authentication Service"],
                    "impact_to_customer": "Complete service disruption for all users",
                    "root_cause": "Database connection pool exhaustion due to misconfigured connection timeout",
                    "resolution": "Emergency configuration change to connection pool settings",
                    "preventative_measures": "Configuration review implemented, but did not address underlying architectural issue"
                },
                "INC-8015": {
                    "date": "2025-04-29",
                    "duration": "2 hours 15 minutes",
                    "affected_services": ["Data Processing Pipeline", "Analytics Dashboard"],
                    "impact_to_customer": "Delayed data processing, stale dashboard information",
                    "root_cause": "Memory leak in data processing service leading to cascading failures",
                    "resolution": "Service restart and emergency patch deployment",
                    "preventative_measures": "Memory optimization implemented, monitoring enhanced"
                },
                "INC-8544": {
                    "date": "2025-05-21",
                    "duration": "4 hours 07 minutes",
                    "affected_services": ["API Gateway", "Authentication Service", "Core Business Logic"],
                    "impact_to_customer": "Complete service disruption for all users",
                    "root_cause": "Network partition in database cluster triggered failover mechanism failure",
                    "resolution": "Manual database cluster recovery, service restart",
                    "preventative_measures": "Under investigation by Database Reliability team"
                }
            },
            "sla_details": {
                "committed_uptime": "99.99% (Standard quarter measurement)",
                "actual_uptime": {
                    "current_quarter": "99.91%",
                    "breach_status": "In breach of SLA"
                },
                "service_credit_terms": {
                    "99.9% - 99.99%": "10% of monthly fee as service credit",
                    "99.5% - 99.9%": "15% of monthly fee as service credit",
                    "Below 99.5%": "25% of monthly fee as service credit"
                },
                "calculated_credit_due": "$31,250 (25% of monthly fee)"
            },
            "technical_remediation_plan": {
                "immediate_actions": [
                    {
                        "action": "Architecture review of database clustering",
                        "owner": "Database Reliability Team",
                        "eta": "Complete within 7 days"
                    },
                    {
                        "action": "Enhanced monitoring deployment",
                        "owner": "SRE Team",
                        "eta": "Complete within 3 days"
                    },
                    {
                        "action": "Circuit breaker implementation for API services",
                        "owner": "Platform Engineering",
                        "eta": "Complete within 10 days"
                    }
                ],
                "medium_term_actions": [
                    {
                        "action": "Database cluster redesign",
                        "owner": "Database Reliability Team",
                        "eta": "Design in 2 weeks, implementation in 4 weeks"
                    },
                    {
                        "action": "Regional failover capability enhancement",
                        "owner": "SRE Team",
                        "eta": "Complete within 4 weeks"
                    },
                    {
                        "action": "Service mesh implementation",
                        "owner": "Platform Engineering",
                        "eta": "Phased over 6 weeks"
                    }
                ],
                "customer_specific_accommodations": [
                    {
                        "action": "Dedicated Slack channel with engineering team",
                        "purpose": "Real-time visibility into service health"
                    },
                    {
                        "action": "Weekly status updates with technical leadership",
                        "purpose": "Transparency on remediation progress"
                    },
                    {
                        "action": "Designated senior engineer during business hours",
                        "purpose": "Immediate response to any issues"
                    },
                    {
                        "action": "Custom monitoring dashboard",
                        "purpose": "Self-service visibility into platform health"
                    }
                ]
            },
            "business_remediation_options": {
                "financial_considerations": {
                    "service_credits": {
                        "standard_amount": "$31,250 (per SLA terms)",
                        "recommended_offer": "$50,000 (goodwill additional credit)"
                    },
                    "contract_adjustments": {
                        "renewal_discount": "5-10% discount on renewal",
                        "term_extension": "18-month term with locked-in pricing",
                        "enhanced_sla": "Custom SLA with higher penalties"
                    }
                },
                "value_adds": {
                    "executive_engagement": {
                        "cto_briefing": "Direct session with company CTO",
                        "quarterly_business_reviews": "Added executive participation",
                        "strategic_roadmap_input": "Priority consideration for feature requests"
                    },
                    "training_and_enablement": {
                        "premium_training": "Complimentary training package ($25,000 value)",
                        "certification_vouchers": "25 certification vouchers for team members",
                        "architectural_review": "Solution architecture review session"
                    },
                    "support_enhancements": {
                        "dedicated_tam": "Temporary dedicated Technical Account Manager",
                        "priority_support": "Front-of-line support for 90 days",
                        "after_hours_support": "Direct emergency line to senior support"
                    }
                },
                "renewal_incentives": {
                    "early_renewal": "Additional 5% discount for early commitment",
                    "multi_year_option": "15% discount for 3-year commitment",
                    "expansion_discount": "Tiered pricing improvements for user growth"
                }
            },
            "communication_strategy": {
                "tone": "Empathetic but confident",
                "key_elements": [
                    "Explicit acknowledgment of impact",
                    "Transparency about root causes",
                    "Concrete action plan with timelines",
                    "Clear ownership and accountability",
                    "Appropriate compensation offer",
                    "Forward-looking partnership framing"
                ],
                "escalation_path": [
                    "Account Executive ownership with support from Solutions Engineering",
                    "VP of Customer Success engagement for relationship repair",
                    "CTO involvement for technical credibility",
                    "CEO communication if necessary for strategic accounts"
                ],
                "follow_up_plan": {
                    "24_hours": "Written summary of discussion and commitments",
                    "72_hours": "Technical remediation plan document",
                    "7_days": "Executive briefing session",
                    "14_days": "First status update on remediation progress",
                    "30_days": "Formal service review and renewal discussion"
                }
            }
        }


class ServiceFailureComplaint(BusinessScenario):
    """
    Service failure complaint scenario.
    
    Tests how well the model handles complaint resolution for a service failure,
    requiring troubleshooting, empathy, and service recovery skills.
    """
    
    def __init__(self, scenario_id: str = "complaint_002"):
        """
        Initialize the service failure complaint scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Delayed Shipment Complaint",
            description="Customer complaining about a significantly delayed shipment with poor communication",
            industry="Retail",
            complexity="medium",
            tools_required=["customer_history", "order_management"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "I'm extremely frustrated with your company right now. I placed an order two weeks ago (order #RT-29873645) for my daughter's birthday present, which was supposed to arrive in 3-5 business days. Her birthday is tomorrow, and the order still shows as 'processing'. I've tried calling customer service twice and spent over an hour on hold each time without getting through. This is completely unacceptable.",
                "expected_tool_calls": [
                    {
                        "tool_id": "order_management",
                        "parameters": {
                            "order_number": "RT-29873645",
                            "lookup_fields": ["status", "items", "shipping_method", "estimated_delivery", "processing_notes"]
                        }
                    }
                ]
            },
            {
                "user_message": "Yes, that's my order. I selected expedited shipping specifically to ensure it would arrive in time for her birthday. The website clearly stated 3-5 business days for delivery with that shipping method. It's now been 10 business days and it hasn't even shipped! What's the point of paying extra for expedited shipping if you can't meet that timeline? I need a solution immediately - her birthday is tomorrow!",
                "expected_tool_calls": [
                    {
                        "tool_id": "customer_history",
                        "parameters": {
                            "order_number": "RT-29873645",
                            "lookup_fields": ["customer_information", "purchase_history", "loyalty_status", "previous_complaints"]
                        }
                    }
                ]
            },
            {
                "user_message": "I appreciate you checking into this and acknowledging the delay. I understand supply chain issues happen, but the lack of proactive communication is what's most frustrating. I could have made alternative arrangements if I had known. At this point, I need to know: 1) Can you expedite shipping to get it here by tomorrow? 2) If not, what compensation are you offering for the inconvenience and the extra I paid for expedited shipping? And 3) How will you prevent this from happening to other customers?",
                "expected_tool_calls": [
                    {
                        "tool_id": "order_management",
                        "parameters": {
                            "action": "shipping_options",
                            "order_number": "RT-29873645",
                            "current_location": "warehouse",
                            "delivery_address": "customer_address",
                            "urgency": "next_day"
                        }
                    }
                ]
            },
            {
                "user_message": "The overnight delivery option would be great, thank you. And I appreciate the refund of the shipping charge plus the additional discount on my next order. I understand these situations happen occasionally, but better communication would have made a big difference. I'll watch for the shipping confirmation and tracking number tonight. If the package arrives tomorrow as promised, I'll consider this resolved.",
                "expected_tool_calls": [
                    {
                        "tool_id": "order_management",
                        "parameters": {
                            "action": "update_order",
                            "order_number": "RT-29873645",
                            "updates": {
                                "shipping_method": "overnight",
                                "shipping_cost": "refunded",
                                "notes": "Escalated due to delay. Customer informed of overnight delivery. Future order discount applied."
                            },
                            "send_confirmations": True
                        }
                    }
                ]
            }
        ]
    
    def _initialize_ground_truth(self) -> Dict[str, Any]:
        """
        Initialize ground truth information.
        
        Returns:
            Dictionary with ground truth data
        """
        return {
            "order_details": {
                "order_number": "RT-29873645",
                "order_date": "2025-05-08",
                "order_total": "$149.95",
                "items": [
                    {
                        "product_id": "TY-5592",
                        "name": "Deluxe Arts and Crafts Set",
                        "price": "$129.99",
                        "quantity": 1,
                        "status": "In stock but on backorder",
                        "inventory_note": "Supply chain delay from manufacturer"
                    },
                    {
                        "product_id": "GW-1123",
                        "name": "Personalized Gift Wrapping",
                        "price": "$9.99",
                        "quantity": 1,
                        "status": "Available"
                    }
                ],
                "shipping_method": {
                    "selected": "Expedited Shipping",
                    "cost": "$9.99",
                    "promised_delivery": "3-5 business days",
                    "actual_status": "Processing - Not shipped"
                },
                "processing_notes": [
                    {
                        "date": "2025-05-08",
                        "note": "Order received and payment processed"
                    },
                    {
                        "date": "2025-05-09",
                        "note": "Inventory allocation failed - item TY-5592 on backorder"
                    },
                    {
                        "date": "2025-05-12",
                        "note": "System flag for delay notification - EMAIL FAILED"
                    },
                    {
                        "date": "2025-05-15",
                        "note": "Backorder received in warehouse, pending processing"
                    },
                    {
                        "date": "2025-05-21",
                        "note": "Order still in processing queue due to warehouse backlog"
                    }
                ],
                "estimated_delivery": {
                    "original": "2025-05-13 to 2025-05-15",
                    "current_estimate": "2025-05-24 to 2025-05-25"
                }
            },
            "customer_information": {
                "name": "Alex Morgan",
                "account_since": "2022-11-03",
                "orders_past_year": 7,
                "total_spent": "$543.88",
                "loyalty_tier": "Silver",
                "previous_complaints": 0,
                "contact_preference": "Email",
                "delivery_address": {
                    "city": "Portland",
                    "state": "OR",
                    "zip": "97205"
                }
            },
            "shipping_options": {
                "warehouse_location": "Seattle, WA",
                "current_status": "Item located and ready for shipping",
                "available_options": [
                    {
                        "method": "Standard Shipping",
                        "estimated_delivery": "2025-05-24 to 2025-05-25",
                        "cost": "$5.99"
                    },
                    {
                        "method": "Expedited Shipping",
                        "estimated_delivery": "2025-05-23",
                        "cost": "$9.99"
                    },
                    {
                        "method": "Overnight Shipping",
                        "estimated_delivery": "2025-05-23 (by end of day)",
                        "cost": "$24.99",
                        "cutoff_time": "2025-05-22 5:00 PM PT"
                    }
                ],
                "delivery_notes": "Package can be sent overnight if processed immediately. Still within cutoff window."
            },
            "service_recovery_options": {
                "shipping_remediation": {
                    "refund_shipping_cost": True,
                    "upgrade_shipping": True,
                    "cost_to_company": "$24.99"
                },
                "compensation_options": {
                    "recommended": {
                        "shipping_refund": "$9.99",
                        "discount_next_order": "20% off next order",
                        "loyalty_points": "500 bonus points"
                    },
                    "alternative": {
                        "partial_refund": "$25 off order",
                        "gift_card": "$25 store credit",
                        "free_gift": "Add complementary item valued at $15-25"
                    }
                },
                "communication_plan": {
                    "immediate": "Personal call or chat to resolve issue",
                    "upon_shipping": "Confirmation email with tracking and apology",
                    "post_delivery": "Follow-up satisfaction check",
                    "future_prevention": "Add to enhanced tracking for next order"
                }
            },
            "process_improvement_insights": {
                "failure_points": [
                    {
                        "issue": "Backorder notification failure",
                        "cause": "Email notification system error",
                        "fix": "Implement redundant notification systems with SMS backup"
                    },
                    {
                        "issue": "No escalation of aging orders",
                        "cause": "Automated flag not triggering manual review",
                        "fix": "Enhance exception reporting for expedited shipping delays"
                    },
                    {
                        "issue": "Customer service accessibility",
                        "cause": "High call volume with insufficient staffing",
                        "fix": "Expand omnichannel support options and callback capability"
                    }
                ],
                "communication_improvements": {
                    "proactive_alerts": "Implement multi-channel notifications for any shipping delay",
                    "transparency": "Add real-time order status tracking with explanations for delays",
                    "expectation_setting": "Clearer inventory status indicators on product pages"
                }
            }
        }


class BillingDisputeScenario(BusinessScenario):
    """
    Billing dispute scenario.
    
    Tests how well the model handles billing disputes requiring investigation,
    policy knowledge, and resolution skills.
    """
    
    def __init__(self, scenario_id: str = "complaint_003"):
        """
        Initialize the billing dispute scenario.
        
        Args:
            scenario_id: Unique identifier for the scenario
        """
        super().__init__(
            scenario_id=scenario_id,
            name="Unexpected Charge Dispute",
            description="Customer disputing an unexpected charge on their account requiring investigation",
            industry="Financial Services",
            complexity="medium",
            tools_required=["customer_history", "order_management"]
        )
    
    def _initialize_conversation(self) -> List[Dict[str, Any]]:
        """
        Initialize the conversation flow.
        
        Returns:
            List of conversation turns
        """
        return [
            {
                "user_message": "I just noticed a charge of $89.99 on my credit card statement from your company, but I don't remember authorizing this payment. I haven't used your services in months. My account number is AC-58721. I want this charge reversed immediately.",
                "expected_tool_calls": [
                    {
                        "tool_id": "customer_history",
                        "parameters": {
                            "account_number": "AC-58721",
                            "lookup_fields": ["subscription_status", "billing_history", "recent_transactions", "account_notes"]
                        }
                    }
                ]
            },
            {
                "user_message": "I definitely didn't receive any emails about an upcoming renewal. I would have canceled it if I had known. I haven't used the service since last year, and I certainly didn't agree to automatic renewal. This feels like a deceptive billing practice.",
                "expected_tool_calls": [
                    {
                        "tool_id": "order_management",
                        "parameters": {
                            "action": "communication_history",
                            "account_number": "AC-58721",
                            "communication_type": "renewal_notification",
                            "time_period": "last_3_months"
                        }
                    }
                ]
            },
            {
                "user_message": "Hmm, I don't recall seeing those emails. They might have gone to spam. But regardless, I haven't used the service in over 6 months. Is there any way you can make an exception in this case? I'd like a full refund since I haven't used any of the services in this renewal period.",
                "expected_tool_calls": [
                    {
                        "tool_id": "customer_history",
                        "parameters": {
                            "account_number": "AC-58721",
                            "lookup_fields": ["usage_data", "login_history", "refund_policy_eligibility"]
                        }
                    }
                ]
            },
            {
                "user_message": "I appreciate your understanding and willingness to provide a full refund in this case. Yes, please go ahead and process the refund to my original payment method. And yes, please cancel my subscription so it doesn't auto-renew again in the future. Thank you for resolving this quickly.",
                "expected_tool_calls": [
                    {
                        "tool_id": "order_management",
                        "parameters": {
                            "action": "process_refund",
                            "account_number": "AC-58721",
                            "refund_amount": "89.99",
                            "refund_reason": "Customer did not intend to renew, service unused",
                            "cancel_subscription": True,
                            "send_confirmation": True
                        }
                    }
                ]
            }
        ]
    
    def _initialize_ground_truth(self) -> Dict[str, Any]:
        """
        Initialize ground truth information.
        
        Returns:
            Dictionary with ground truth data
        """
        return {
            "account_information": {
                "account_number": "AC-58721",
                "customer_name": "Sam Taylor",
                "account_created": "2023-03-15",
                "subscription_details": {
                    "plan": "Premium Annual",
                    "price": "$89.99/year",
                    "status": "Active - Recently Renewed",
                    "renewal_date": "2025-05-15",
                    "previous_renewal": "2024-05-15",
                    "auto_renewal": "Enabled (default setting)",
                    "cancellation_policy": "Full refund available within 14 days of renewal if unused"
                },
                "billing_history": [
                    {
                        "date": "2025-05-15",
                        "description": "Premium Annual Plan Renewal",
                        "amount": "$89.99",
                        "payment_method": "Visa ending in 4578",
                        "status": "Processed"
                    },
                    {
                        "date": "2024-05-15",
                        "description": "Premium Annual Plan Renewal",
                        "amount": "$79.99",
                        "payment_method": "Visa ending in 4578",
                        "status": "Processed"
                    },
                    {
                        "date": "2023-05-15",
                        "description": "Premium Annual Plan - New Subscription",
                        "amount": "$79.99",
                        "payment_method": "Visa ending in 4578",
                        "status": "Processed"
                    }
                ],
                "account_notes": [
                    {
                        "date": "2024-08-03",
                        "note": "Customer contacted support for feature assistance. Issue resolved."
                    },
                    {
                        "date": "2023-06-12",
                        "note": "Customer requested password reset. Completed."
                    }
                ]
            },
            "usage_data": {
                "last_login": "2024-10-22 (203 days ago)",
                "login_frequency": {
                    "past_30_days": 0,
                    "past_90_days": 0,
                    "past_180_days": 0,
                    "past_365_days": 4
                },
                "feature_usage": {
                    "past_30_days": "None",
                    "past_90_days": "None",
                    "past_180_days": "Minimal - 2 document exports on 2024-10-22"
                }
            },
            "communication_history": {
                "renewal_notifications": [
                    {
                        "date": "2025-04-15",
                        "type": "Email",
                        "subject": "Your Premium Subscription Renews in 30 Days",
                        "delivery_status": "Delivered",
                        "open_status": "Not opened"
                    },
                    {
                        "date": "2025-05-01",
                        "type": "Email",
                        "subject": "Reminder: Your Premium Subscription Renews Soon",
                        "delivery_status": "Delivered",
                        "open_status": "Not opened"
                    },
                    {
                        "date": "2025-05-08",
                        "type": "Email",
                        "subject": "Final Notice: Your Premium Subscription Renews in 7 Days",
                        "delivery_status": "Delivered",
                        "open_status": "Not opened"
                    }
                ],
                "other_communications": [
                    {
                        "date": "2025-05-16",
                        "type": "Email",
                        "subject": "Thank You for Your Renewal",
                        "delivery_status": "Delivered",
                        "open_status": "Not opened"
                    }
                ]
            },
            "policy_information": {
                "refund_eligibility": {
                    "days_since_charge": 7,
                    "within_refund_window": True,
                    "standard_policy": "Full refund if within 14 days of renewal",
                    "usage_based_exception": "Eligible - No usage in current billing period"
                },
                "cancellation_terms": {
                    "cancellation_fee": "None if subscription canceled during refund window",
                    "prorated_refund": "Not applicable for annual subscriptions past refund window",
                    "future_renewal": "Subscription can be canceled to prevent future renewals"
                },
                "renewal_terms": {
                    "notification_requirement": "At least three notifications prior to renewal",
                    "opt_out_method": "Cancel via account settings or customer support",
                    "term_change_options": "Can downgrade or switch to monthly before next renewal"
                }
            },
            "resolution_options": {
                "recommended_action": {
                    "refund_amount": "Full refund ($89.99)",
                    "justification": "Within refund window with no usage in current period",
                    "goodwill_factor": "Long-term customer with minimal recent engagement"
                },
                "subscription_options": {
                    "cancel_subscription": "Prevent future renewals",
                    "downgrade_option": "Offer basic tier at $39.99/year",
                    "pause_option": "Not available for this subscription type"
                },
                "customer_retention": {
                    "win_back_offer": "3 months free if reactivate within 90 days",
                    "feedback_request": "Send post-cancellation survey",
                    "reactivation_process": "Simplified one-click reactivation via email link"
                }
            },
            "process_improvement_insights": {
                "notification_effectiveness": {
                    "issue": "Low open rate on renewal emails",
                    "enhancement": "Add SMS notification option for critical billing alerts"
                },
                "user_engagement": {
                    "issue": "No proactive outreach for inactive accounts",
                    "enhancement": "Implement engagement campaign for accounts with no activity for 90+ days"
                },
                "renewal_transparency": {
                    "issue": "Renewal notifications could be more prominent",
                    "enhancement": "Add renewal information to login screen for accounts nearing renewal"
                }
            }
        }