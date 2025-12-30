# ---------------------------------------------------------------------
# ai/services/vitals_trend_analyzer.py
# ---------------------------------------------------------------------
# Vitals Trend Analyzer
# Analyzes vital sign trends over time using statistical methods
# Wraps existing app/db/vitals query functions
# ---------------------------------------------------------------------

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, TYPE_CHECKING
import logging
from app.db.vitals import get_patient_vitals

if TYPE_CHECKING:
    from fastapi import Request

logger = logging.getLogger(__name__)


class VitalsTrendAnalyzer:
    """
    Analyzes vital sign trends over time using statistical methods.

    Provides trend analysis (linear regression), comparison against clinical norms,
    and actionable insights for clinicians.

    Vista Data Integration:
    - If request context is provided, analyzer will check for cached Vista data
    - Cached Vista data is automatically used if available (from "Refresh from Vista")
    - Falls back to PostgreSQL-only data if no Vista cache exists
    """

    def __init__(self, patient_icn: str, request: Optional["Request"] = None):
        """
        Initialize analyzer for a specific patient.

        Args:
            patient_icn: Patient's Integrated Care Number
            request: Optional FastAPI request for Vista cache access
        """
        self.patient_icn = patient_icn
        self.request = request

    def analyze_trends(self, days: int = 90) -> Dict[str, Any]:
        """
        Analyze vital sign trends over specified period.

        Args:
            days: Number of days to analyze (default 90)

        Returns:
            Dictionary with trend analysis for each vital sign:
            {
                'total_readings': int,
                'date_range': str,
                'bp': {...},
                'hr': {...},
                'temp': {...},
                'weight': {...},
                'error': str (optional)
            }
        """
        logger.info(f"Analyzing vital trends for patient {self.patient_icn} over last {days} days")

        try:
            # Try to get cached Vista data first (if user has refreshed from Vista)
            all_vitals = None
            data_source = "PostgreSQL"

            if self.request:
                from app.services.vista_cache import VistaSessionCache
                cached = VistaSessionCache.get_cached_data(
                    self.request,
                    self.patient_icn,
                    "vitals"
                )

                if cached and "vista_responses" in cached:
                    # Merge PG data with cached Vista responses
                    from app.services.realtime_overlay import merge_vitals_data
                    pg_vitals = get_patient_vitals(self.patient_icn, limit=500)
                    all_vitals, merge_stats = merge_vitals_data(
                        pg_vitals,
                        cached["vista_responses"],
                        self.patient_icn
                    )
                    data_source = f"PostgreSQL + Vista ({', '.join(cached.get('sites', []))})"
                    logger.info(
                        f"Using cached Vista vitals: {merge_stats['total_merged']} records "
                        f"({merge_stats['pg_count']} PG + {merge_stats['vista_count']} Vista from {len(cached.get('sites', []))} sites)"
                    )

            # Fallback to PostgreSQL if no Vista cache
            if all_vitals is None:
                all_vitals = get_patient_vitals(self.patient_icn, limit=500)
                logger.info(f"Using PostgreSQL vitals data: {len(all_vitals)} records")

            if not all_vitals:
                return {
                    'error': f'No vitals data available for patient {self.patient_icn}',
                    'total_readings': 0,
                    'data_source': data_source
                }

            # Filter to date range
            cutoff_date = datetime.now() - timedelta(days=days)
            filtered_vitals = []

            for vital in all_vitals:
                if vital.get('taken_datetime'):
                    try:
                        taken_dt = datetime.fromisoformat(vital['taken_datetime'])
                        if taken_dt >= cutoff_date:
                            filtered_vitals.append(vital)
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Invalid datetime format: {vital.get('taken_datetime')}: {e}")
                        continue

            if not filtered_vitals:
                return {
                    'error': f'No vitals data in the last {days} days',
                    'total_readings': 0
                }

            # Calculate date range
            dates = sorted([
                datetime.fromisoformat(v['taken_datetime'])
                for v in filtered_vitals
                if v.get('taken_datetime')
            ])
            date_range = f"{dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}"

            # Analyze each vital type
            result = {
                'total_readings': len(filtered_vitals),
                'date_range': date_range,
                'period_days': days,
                'data_source': data_source  # Include Vista sites if cached data was used
            }

            # Blood Pressure
            bp_analysis = self._analyze_bp(filtered_vitals)
            if bp_analysis:
                result['bp'] = bp_analysis

            # Heart Rate (Pulse)
            hr_analysis = self._analyze_hr(filtered_vitals)
            if hr_analysis:
                result['hr'] = hr_analysis

            # Temperature
            temp_analysis = self._analyze_temp(filtered_vitals)
            if temp_analysis:
                result['temp'] = temp_analysis

            # Weight (optional, if data available)
            weight_analysis = self._analyze_weight(filtered_vitals)
            if weight_analysis:
                result['weight'] = weight_analysis

            return result

        except Exception as e:
            logger.error(f"Error analyzing vital trends for patient {self.patient_icn}: {e}", exc_info=True)
            return {
                'error': f'Error analyzing vital trends: {str(e)}',
                'total_readings': 0
            }

    def _analyze_bp(self, vitals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze blood pressure trends."""
        # Extract BP readings
        bp_readings = []
        for v in vitals:
            if v.get('systolic') is not None and v.get('diastolic') is not None:
                bp_readings.append({
                    'datetime': datetime.fromisoformat(v['taken_datetime']),
                    'systolic': v['systolic'],
                    'diastolic': v['diastolic']
                })

        if not bp_readings:
            return None

        # Sort by date
        bp_readings.sort(key=lambda x: x['datetime'])

        # Extract arrays for analysis
        systolic = np.array([r['systolic'] for r in bp_readings])
        diastolic = np.array([r['diastolic'] for r in bp_readings])

        # Calculate statistics
        avg_sys = np.mean(systolic)
        avg_dia = np.mean(diastolic)

        # Linear regression for trend
        x = np.arange(len(systolic))
        slope_sys = 0
        slope_dia = 0

        if len(systolic) > 1:
            slope_sys = np.polyfit(x, systolic, 1)[0]
            slope_dia = np.polyfit(x, diastolic, 1)[0]

        # Interpret trend (change per reading * total readings = total change)
        total_change_sys = slope_sys * len(systolic)

        if total_change_sys > 10:
            trend = f"Increasing (up {total_change_sys:.0f} mmHg systolic over period)"
            status = "concerning"
        elif total_change_sys < -10:
            trend = f"Decreasing (down {abs(total_change_sys):.0f} mmHg systolic over period)"
            status = "improving"
        else:
            trend = "Stable"
            status = "normal"

        # Check against clinical norms
        # Stage 1 Hypertension: 130-139 systolic or 80-89 diastolic
        # Stage 2 Hypertension: >=140 systolic or >=90 diastolic
        if avg_sys >= 140 or avg_dia >= 90:
            interpretation = f"Elevated - Stage 2 Hypertension range (avg {avg_sys:.0f}/{avg_dia:.0f} mmHg)"
            clinical_note = "Consider medication adjustment or initiation per HTN guidelines"
            status = "concerning"
        elif avg_sys >= 130 or avg_dia >= 80:
            interpretation = f"Elevated - Stage 1 Hypertension range (avg {avg_sys:.0f}/{avg_dia:.0f} mmHg)"
            clinical_note = "Monitor closely, consider lifestyle modifications"
            status = "elevated"
        else:
            interpretation = f"Well-controlled (avg {avg_sys:.0f}/{avg_dia:.0f} mmHg)"
            clinical_note = "Continue current management"

        return {
            'avg_systolic': f"{avg_sys:.0f}",
            'avg_diastolic': f"{avg_dia:.0f}",
            'reading_count': len(bp_readings),
            'trend_description': trend,
            'interpretation': interpretation,
            'clinical_note': clinical_note,
            'status': status,
            'first_reading': f"{bp_readings[0]['systolic']}/{bp_readings[0]['diastolic']}",
            'last_reading': f"{bp_readings[-1]['systolic']}/{bp_readings[-1]['diastolic']}"
        }

    def _analyze_hr(self, vitals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze heart rate (pulse) trends."""
        # Extract pulse readings (can be in either numeric_value for PULSE type or elsewhere)
        hr_readings = []

        for v in vitals:
            pulse_value = None

            # Check vital_type for PULSE
            if v.get('vital_type') == 'PULSE' and v.get('numeric_value') is not None:
                pulse_value = v['numeric_value']
            # Some systems store pulse in result_value
            elif v.get('vital_abbr') == 'P' and v.get('numeric_value') is not None:
                pulse_value = v['numeric_value']

            if pulse_value is not None:
                hr_readings.append({
                    'datetime': datetime.fromisoformat(v['taken_datetime']),
                    'pulse': pulse_value
                })

        if not hr_readings:
            return None

        # Sort by date
        hr_readings.sort(key=lambda x: x['datetime'])

        # Extract array
        pulse = np.array([r['pulse'] for r in hr_readings])

        # Calculate statistics
        avg_hr = np.mean(pulse)

        # Linear regression for trend
        x = np.arange(len(pulse))
        slope = 0

        if len(pulse) > 1:
            slope = np.polyfit(x, pulse, 1)[0]

        # Interpret trend
        total_change = slope * len(pulse)

        if total_change > 10:
            trend = f"Increasing (up {total_change:.0f} bpm over period)"
            status = "concerning"
        elif total_change < -10:
            trend = f"Decreasing (down {abs(total_change):.0f} bpm over period)"
            status = "improving"
        else:
            trend = "Stable"
            status = "normal"

        # Check clinical norms
        # Tachycardia: >100 bpm
        # Bradycardia: <50 bpm (if not on beta-blocker)
        # Normal: 60-100 bpm
        if avg_hr > 100:
            interpretation = "Tachycardic (elevated heart rate)"
            clinical_note = "Consider causes: pain, anxiety, medications, thyroid, infection, dehydration"
            status = "concerning"
        elif avg_hr < 50:
            interpretation = "Bradycardic (low heart rate)"
            clinical_note = "Verify beta-blocker dose if applicable; consider cardiac workup if symptomatic"
            status = "concerning"
        else:
            interpretation = "Normal sinus rhythm"
            clinical_note = "Heart rate within normal limits"

        return {
            'avg': f"{avg_hr:.0f}",
            'reading_count': len(hr_readings),
            'trend_description': trend,
            'interpretation': interpretation,
            'clinical_note': clinical_note,
            'status': status,
            'first_reading': f"{hr_readings[0]['pulse']:.0f}",
            'last_reading': f"{hr_readings[-1]['pulse']:.0f}"
        }

    def _analyze_temp(self, vitals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze temperature trends."""
        # Extract temperature readings
        temp_readings = []

        for v in vitals:
            temp_value = None

            # Check vital_type for TEMPERATURE
            if v.get('vital_type') == 'TEMPERATURE' and v.get('numeric_value') is not None:
                temp_value = v['numeric_value']
            elif v.get('vital_abbr') == 'T' and v.get('numeric_value') is not None:
                temp_value = v['numeric_value']

            if temp_value is not None:
                temp_readings.append({
                    'datetime': datetime.fromisoformat(v['taken_datetime']),
                    'temp': temp_value
                })

        if not temp_readings:
            return None

        # Sort by date
        temp_readings.sort(key=lambda x: x['datetime'])

        # Extract array
        temps = np.array([r['temp'] for r in temp_readings])

        # Calculate statistics
        avg_temp = np.mean(temps)
        max_temp = np.max(temps)

        # Count febrile episodes (>100.4°F)
        febrile_count = np.sum(temps > 100.4)

        # Interpret
        if max_temp > 100.4:
            interpretation = f"Febrile episodes detected ({febrile_count} reading(s) >100.4°F, max {max_temp:.1f}°F)"
            clinical_note = "Evaluate for source of fever; consider infectious workup"
            status = "concerning"
        elif avg_temp > 99.5:
            interpretation = f"Slightly elevated average temperature ({avg_temp:.1f}°F)"
            clinical_note = "Monitor for fever; may be within normal variation"
            status = "elevated"
        else:
            interpretation = f"Afebrile, stable (avg {avg_temp:.1f}°F)"
            clinical_note = "Temperature within normal limits"
            status = "normal"

        return {
            'avg': f"{avg_temp:.1f}",
            'max': f"{max_temp:.1f}",
            'reading_count': len(temp_readings),
            'febrile_count': int(febrile_count),
            'interpretation': interpretation,
            'clinical_note': clinical_note,
            'status': status
        }

    def _analyze_weight(self, vitals: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze weight trends."""
        # Extract weight readings
        weight_readings = []

        for v in vitals:
            weight_value = None

            # Check vital_type for WEIGHT
            if v.get('vital_type') == 'WEIGHT' and v.get('numeric_value') is not None:
                weight_value = v['numeric_value']
            elif v.get('vital_abbr') == 'WT' and v.get('numeric_value') is not None:
                weight_value = v['numeric_value']

            if weight_value is not None:
                weight_readings.append({
                    'datetime': datetime.fromisoformat(v['taken_datetime']),
                    'weight': weight_value
                })

        if not weight_readings:
            return None

        # Sort by date
        weight_readings.sort(key=lambda x: x['datetime'])

        # Extract array
        weights = np.array([r['weight'] for r in weight_readings])

        # Calculate statistics
        avg_weight = np.mean(weights)
        first_weight = weights[0]
        last_weight = weights[-1]
        weight_change = last_weight - first_weight
        percent_change = (weight_change / first_weight) * 100

        # Linear regression for trend
        x = np.arange(len(weights))
        slope = 0

        if len(weights) > 1:
            slope = np.polyfit(x, weights, 1)[0]

        # Interpret trend
        # Concerning if >5% change over period
        if abs(percent_change) > 10:
            if weight_change > 0:
                interpretation = f"Significant weight gain ({weight_change:.1f} lbs, {percent_change:.1f}%)"
                clinical_note = "Consider causes: fluid retention (CHF, renal), medication side effects, dietary changes"
                status = "concerning"
            else:
                interpretation = f"Significant weight loss ({abs(weight_change):.1f} lbs, {abs(percent_change):.1f}%)"
                clinical_note = "Consider causes: malnutrition, malignancy, hyperthyroidism, depression"
                status = "concerning"
        elif abs(percent_change) > 5:
            if weight_change > 0:
                interpretation = f"Moderate weight gain ({weight_change:.1f} lbs, {percent_change:.1f}%)"
                clinical_note = "Monitor trend; consider dietary counseling"
                status = "elevated"
            else:
                interpretation = f"Moderate weight loss ({abs(weight_change):.1f} lbs, {abs(percent_change):.1f}%)"
                clinical_note = "Monitor trend; assess if intentional"
                status = "elevated"
        else:
            interpretation = f"Stable weight (avg {avg_weight:.1f} lbs, change {weight_change:+.1f} lbs)"
            clinical_note = "Weight stable within normal variation"
            status = "normal"

        return {
            'avg': f"{avg_weight:.1f}",
            'first_weight': f"{first_weight:.1f}",
            'last_weight': f"{last_weight:.1f}",
            'change': f"{weight_change:+.1f}",
            'percent_change': f"{percent_change:+.1f}",
            'reading_count': len(weight_readings),
            'interpretation': interpretation,
            'clinical_note': clinical_note,
            'status': status
        }
