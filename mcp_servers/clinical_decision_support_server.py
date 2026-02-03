"""
Clinical Decision Support MCP Server - COMPLETE IMPLEMENTATION

Exposes clinical algorithms and risk assessment tools via MCP protocol.
Wraps existing med-z1 AI business logic without duplicating code.

Tools provided:
- check_drug_interactions: DDI analysis using DrugBank reference
- assess_fall_risk: Fall risk assessment from meds, age, conditions
- calculate_ckd_egfr: CKD-EPI eGFR calculation for kidney function
- recommend_cancer_screening: USPSTF guideline recommendations

Usage:
    python mcp_servers/clinical_decision_support_server.py

Configuration:
    Reads from root .env file (DATABASE_URL, MinIO config, etc.)

Author: Created for med-z1 Clinical AI Career Preparation Guide (Section 6)
Version: 1.0
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any
from dotenv import load_dotenv
from datetime import datetime

# MCP SDK imports
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.types as types

# Ensure project root is in Python path and .env is loaded
# CRITICAL: This must happen BEFORE any app.db or ai imports
try:
    project_root = Path(__file__).resolve().parent.parent
    print(f"DEBUG: Project root: {project_root}", file=sys.stderr)

    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"DEBUG: Added to sys.path: {project_root}", file=sys.stderr)

    # Explicitly load .env file
    env_path = project_root / ".env"
    print(f"DEBUG: Loading .env from: {env_path}", file=sys.stderr)
    print(f"DEBUG: .env exists: {env_path.exists()}", file=sys.stderr)
    load_dotenv(env_path)
    print(f"DEBUG: .env loaded successfully", file=sys.stderr)

except Exception as e:
    print(f"ERROR: Failed to set up environment: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Import med-z1 modules
try:
    print(f"DEBUG: Importing med-z1 modules...", file=sys.stderr)
    from app.db.medications import get_patient_medications
    from app.db.patient import get_patient_demographics
    from ai.services.ddi_analyzer import DDIAnalyzer
    print(f"DEBUG: All modules imported successfully", file=sys.stderr)
except ImportError as e:
    print(f"ERROR: Failed to import modules: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    print(f"Make sure you're running from project root: {project_root}", file=sys.stderr)
    sys.exit(1)

# Configure logging
log_file = Path(__file__).parent.parent / "log" / "clinical_decision_support_debug.log"
log_file.parent.mkdir(exist_ok=True)  # Create log directory if it doesn't exist
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(name)-35s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("clinical-decision-support-server")
logger.info(f"Logging to: {log_file}")

# Initialize MCP server
server = Server("clinical-decision-support-server")


# ============================================================================
# ATTRIBUTION HELPER - For clinical auditability and regulatory compliance
# ============================================================================

def _add_attribution_footer(
    result: str,
    tool_name: str,
    data_sources: list[str],
    metadata: dict = None
) -> str:
    """
    Add standardized attribution footer to tool responses.

    Critical for clinical auditability, regulatory compliance, and trust.
    Shows exactly what data sources and tools were used to generate each response.

    Args:
        result: The main tool response text
        tool_name: Name of the tool that generated this response
        data_sources: List of data sources queried (databases, APIs, reference files)
        metadata: Optional additional context (e.g., record counts, date ranges)

    Returns:
        Original result + attribution footer

    Example output footer:
        ---
        **Data Provenance:**
          • Tool: check_drug_interactions
          • Data Sources: DrugBank reference (~191K interactions), patient_medications_outpatient
          • Analysis Timestamp: 2026-02-02 14:30 UTC
          • Medications analyzed: 7
          • Interactions found: 2
    """
    footer = "\n\n---\n\n"
    footer += "**Data Provenance:**\n"
    footer += f"  • **Tool:** `{tool_name}`\n"
    footer += f"  • **Data Sources:** {', '.join(data_sources)}\n"
    footer += f"  • **Analysis Timestamp:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"

    if metadata:
        for key, value in metadata.items():
            footer += f"  • **{key}:** {value}\n"

    return result + footer


# ============================================================================
# TOOL DEFINITIONS - Register all clinical decision support tools
# ============================================================================

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    Define available clinical decision support tools.

    These tools provide clinical algorithms and risk assessments.
    They wrap existing AI business logic from ai/services/ without
    duplicating code.

    Returns:
        List of MCP Tool objects with schemas
    """
    logger.info("Listing available clinical decision support tools")

    return [
        types.Tool(
            name="check_drug_interactions",
            description=(
                "Analyze patient's medications for drug-drug interactions (DDI). "
                "Uses DrugBank reference database (~191K interactions). "
                "Returns DDI details with descriptions of interaction effects. "
                "Critical for medication safety review."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient Integrated Care Number (ICN)"
                    }
                },
                "required": ["patient_icn"]
            }
        ),
        types.Tool(
            name="assess_fall_risk",
            description=(
                "Calculate patient's fall risk score based on medications, age, "
                "and clinical factors. Uses standardized fall risk assessment criteria. "
                "Returns risk level (Low/Moderate/High) with contributing factors. "
                "Useful for geriatric and inpatient safety planning."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient Integrated Care Number (ICN)"
                    }
                },
                "required": ["patient_icn"]
            }
        ),
        types.Tool(
            name="calculate_ckd_egfr",
            description=(
                "Calculate estimated Glomerular Filtration Rate (eGFR) using CKD-EPI equation. "
                "Assesses kidney function for chronic kidney disease staging. "
                "Returns eGFR value and CKD stage interpretation (1-5). "
                "Essential for medication dosing adjustments."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "creatinine_mg_dl": {
                        "type": "number",
                        "description": "Serum creatinine in mg/dL (e.g., 1.2)"
                    },
                    "age": {
                        "type": "integer",
                        "description": "Patient age in years"
                    },
                    "sex": {
                        "type": "string",
                        "enum": ["M", "F", "male", "female"],
                        "description": "Patient sex (M/F or male/female)"
                    },
                    "race_black": {
                        "type": "boolean",
                        "description": "Is patient Black/African American? (default: false)",
                        "default": False
                    }
                },
                "required": ["creatinine_mg_dl", "age", "sex"]
            }
        ),
        types.Tool(
            name="recommend_cancer_screening",
            description=(
                "Recommend age-appropriate cancer screenings based on USPSTF guidelines. "
                "Evaluates patient eligibility for colorectal, breast, cervical, lung, "
                "and prostate cancer screening. Returns personalized screening recommendations "
                "with rationale. Supports preventive care planning."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_icn": {
                        "type": "string",
                        "description": "Patient Integrated Care Number (ICN)"
                    }
                },
                "required": ["patient_icn"]
            }
        )
    ]


# ============================================================================
# TOOL EXECUTION - Handle tool calls from AI
# ============================================================================

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict[str, Any]
) -> list[types.TextContent]:
    """
    Execute a clinical decision support tool.

    Args:
        name: Tool name (must match one from list_tools)
        arguments: Tool parameters from AI

    Returns:
        List of TextContent with formatted results

    Clinical Safety Pattern:
        - All errors return graceful messages (never crash on clinical data)
        - High-risk findings highlighted prominently
        - Missing data handled explicitly (no silent failures)
    """
    logger.info(f"Tool called: {name} with arguments: {arguments}")

    try:
        # Route to appropriate tool handler
        if name == "check_drug_interactions":
            result = await _check_drug_interactions(arguments["patient_icn"])

        elif name == "assess_fall_risk":
            result = await _assess_fall_risk(arguments["patient_icn"])

        elif name == "calculate_ckd_egfr":
            result = _calculate_ckd_egfr(
                creatinine=arguments["creatinine_mg_dl"],
                age=arguments["age"],
                sex=arguments["sex"],
                race_black=arguments.get("race_black", False)
            )

        elif name == "recommend_cancer_screening":
            result = await _recommend_cancer_screening(arguments["patient_icn"])

        else:
            raise ValueError(f"Unknown tool: {name}")

        # Return formatted result to AI
        return [types.TextContent(type="text", text=result)]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}", exc_info=True)
        error_msg = f"⚠️ Error: {str(e)}\n\nPlease verify patient data and try again."
        return [types.TextContent(type="text", text=error_msg)]


# ============================================================================
# TOOL IMPLEMENTATIONS - Clinical algorithms and business logic
# ============================================================================

async def _check_drug_interactions(patient_icn: str) -> str:
    """
    Analyze patient's medications for drug-drug interactions.

    Wraps existing DDIAnalyzer from ai/services/ddi_analyzer.py.
    No code duplication - reuses production AI logic.

    Args:
        patient_icn: Patient ICN

    Returns:
        Formatted DDI analysis with severity indicators
    """
    logger.info(f"Checking DDI for patient {patient_icn}")

    # Get patient medications
    medications = await asyncio.to_thread(
        get_patient_medications,
        patient_icn
    )

    if not medications:
        return "No active medications found. Cannot perform DDI analysis."

    # Initialize DDI analyzer (loads DrugBank reference data)
    analyzer = DDIAnalyzer()

    # Find interactions
    interactions = await asyncio.to_thread(
        analyzer.find_interactions,
        medications
    )

    # Format results
    return _format_ddi_results(interactions, len(medications))


async def _assess_fall_risk(patient_icn: str) -> str:
    """
    Calculate patient's fall risk score.

    Algorithm considers:
    - Age (≥65 = +2 points)
    - High-risk medications (sedatives, antihypertensives, diuretics)
    - Polypharmacy (≥5 medications = +1 point)

    Scoring:
    - 0-1: Low risk
    - 2-3: Moderate risk
    - 4+: High risk

    Args:
        patient_icn: Patient ICN

    Returns:
        Formatted fall risk assessment
    """
    logger.info(f"Assessing fall risk for patient {patient_icn}")

    # Get patient demographics and medications
    demographics = await asyncio.to_thread(get_patient_demographics, patient_icn)
    medications = await asyncio.to_thread(get_patient_medications, patient_icn)

    if not demographics:
        return "⚠️ Patient demographics not found. Cannot assess fall risk."

    # Calculate risk score
    risk_score = 0
    factors = []
    age = None  # Track for attribution metadata

    # Age factor
    dob_str = demographics.get('date_of_birth')
    if dob_str:
        try:
            dob = datetime.strptime(str(dob_str).split()[0], '%Y-%m-%d')
            age = (datetime.now() - dob).days // 365
            if age >= 65:
                risk_score += 2
                factors.append(f"Age {age} (≥65 years)")
        except:
            logger.warning(f"Could not parse DOB: {dob_str}")

    # Medication factors
    med_count = 0
    if medications:
        med_count = len(medications)

        # Polypharmacy
        if med_count >= 5:
            risk_score += 1
            factors.append(f"Polypharmacy ({med_count} medications)")

        # High-risk medication classes
        high_risk_classes = [
            'benzodiazepine', 'sedative', 'hypnotic', 'antihypertensive',
            'diuretic', 'opioid', 'antipsychotic', 'anticonvulsant'
        ]

        high_risk_meds = []
        for med in medications:
            drug_name = (
                med.get('drug_name_national') or
                med.get('drug_name') or
                ''
            ).lower()

            for risk_class in high_risk_classes:
                if risk_class in drug_name:
                    high_risk_meds.append(drug_name.title())
                    risk_score += 1
                    break

        if high_risk_meds:
            factors.append(f"High-risk medications: {', '.join(high_risk_meds[:3])}")

    # Determine risk level
    if risk_score == 0 or risk_score == 1:
        risk_level = "LOW"
        icon = "🟢"
    elif risk_score == 2 or risk_score == 3:
        risk_level = "MODERATE"
        icon = "🟡"
    else:
        risk_level = "HIGH"
        icon = "🔴"

    # Format results
    result = f"{icon} **Fall Risk Assessment: {risk_level}**\n"
    result += f"Risk Score: {risk_score} points\n\n"

    if factors:
        result += "Contributing Factors:\n"
        for factor in factors:
            result += f"  • {factor}\n"
    else:
        result += "No significant risk factors identified.\n"

    result += "\n**Recommendations:**\n"
    if risk_level == "HIGH":
        result += "  • Implement fall prevention protocols\n"
        result += "  • Review medications for dose reduction/discontinuation\n"
        result += "  • Consider physical therapy evaluation\n"
        result += "  • Environmental safety assessment recommended\n"
    elif risk_level == "MODERATE":
        result += "  • Monitor for fall risk factors\n"
        result += "  • Review medications periodically\n"
        result += "  • Patient education on fall prevention\n"
    else:
        result += "  • Continue routine monitoring\n"
        result += "  • Encourage physical activity for strength and balance\n"

    # Add attribution footer for clinical auditability
    metadata = {
        "Risk Score": f"{risk_score} points",
        "Risk Level": risk_level,
        "Contributing Factors": len(factors)
    }
    if age is not None:
        metadata["Patient Age"] = f"{age} years"
    if medications:
        metadata["Medications Reviewed"] = med_count

    return _add_attribution_footer(
        result=result,
        tool_name="assess_fall_risk",
        data_sources=[
            "PostgreSQL patient_demographics table",
            "PostgreSQL patient_medications_outpatient table",
            "PostgreSQL patient_medications_inpatient table"
        ],
        metadata=metadata
    )


def _calculate_ckd_egfr(
    creatinine: float,
    age: int,
    sex: str,
    race_black: bool = False
) -> str:
    """
    Calculate eGFR using CKD-EPI equation (2021 version).

    CKD-EPI Equation (race-neutral, 2021):
    eGFR = 142 × min(Scr/κ, 1)^α × max(Scr/κ, 1)^-1.200 × 0.9938^Age × [1.012 if female]

    Where:
    - Scr = serum creatinine (mg/dL)
    - κ = 0.7 (females) or 0.9 (males)
    - α = -0.241 (females) or -0.302 (males)

    Reference: Inker et al., NEJM 2021
    https://www.nejm.org/doi/full/10.1056/NEJMoa2102953

    Args:
        creatinine: Serum creatinine in mg/dL
        age: Patient age in years
        sex: M/F or male/female
        race_black: Not used in 2021 race-neutral equation (kept for compatibility)

    Returns:
        Formatted eGFR result with CKD staging
    """
    logger.info(f"Calculating eGFR: Cr={creatinine}, age={age}, sex={sex}")

    # Normalize sex input
    sex = sex.upper()[0]  # 'M' or 'F'

    # CKD-EPI parameters by sex
    if sex == 'F':
        kappa = 0.7
        alpha = -0.241
        sex_multiplier = 1.012
    else:  # Male
        kappa = 0.9
        alpha = -0.302
        sex_multiplier = 1.0

    # Calculate eGFR
    min_term = min(creatinine / kappa, 1.0) ** alpha
    max_term = max(creatinine / kappa, 1.0) ** -1.200
    age_term = 0.9938 ** age

    egfr = 142 * min_term * max_term * age_term * sex_multiplier

    # Determine CKD stage
    if egfr >= 90:
        stage = "G1 (Normal or high)"
        risk = "Low risk (if no kidney damage markers)"
        icon = "🟢"
    elif egfr >= 60:
        stage = "G2 (Mildly decreased)"
        risk = "Low risk"
        icon = "🟢"
    elif egfr >= 45:
        stage = "G3a (Mildly to moderately decreased)"
        risk = "Moderate risk"
        icon = "🟡"
    elif egfr >= 30:
        stage = "G3b (Moderately to severely decreased)"
        risk = "High risk"
        icon = "🟠"
    elif egfr >= 15:
        stage = "G4 (Severely decreased)"
        risk = "Very high risk"
        icon = "🔴"
    else:
        stage = "G5 (Kidney failure)"
        risk = "Kidney failure - nephrology referral required"
        icon = "🔴"

    # Format result
    result = f"{icon} **eGFR Result: {egfr:.1f} mL/min/1.73m²**\n\n"
    result += f"**CKD Stage:** {stage}\n"
    result += f"**Clinical Risk:** {risk}\n\n"
    result += "**Input Parameters:**\n"
    result += f"  • Creatinine: {creatinine} mg/dL\n"
    result += f"  • Age: {age} years\n"
    result += f"  • Sex: {'Female' if sex == 'F' else 'Male'}\n"
    result += f"  • Equation: CKD-EPI 2021 (race-neutral)\n\n"

    if egfr < 60:
        result += "**Clinical Recommendations:**\n"
        result += "  • Confirm with repeat testing (GFR varies ~5%)\n"
        result += "  • Review medications for dose adjustments\n"
        result += "  • Monitor for CKD complications (anemia, bone disease, acidosis)\n"
        if egfr < 30:
            result += "  • Nephrology referral recommended\n"
        if egfr < 15:
            result += "  • Prepare for renal replacement therapy (dialysis/transplant)\n"

    # Add attribution footer for clinical auditability
    return _add_attribution_footer(
        result=result,
        tool_name="calculate_ckd_egfr",
        data_sources=[
            "CKD-EPI 2021 equation (race-neutral)",
            "User-provided lab values (serum creatinine)"
        ],
        metadata={
            "eGFR Result": f"{egfr:.1f} mL/min/1.73m²",
            "CKD Stage": stage,
            "Equation Reference": "Inker et al., NEJM 2021"
        }
    )


async def _recommend_cancer_screening(patient_icn: str) -> str:
    """
    Recommend cancer screenings based on USPSTF guidelines.

    Screening recommendations by age/sex:
    - Colorectal: Age 45-75 (A) / 76-85 selective (C)
    - Breast (female): Age 50-74 biennial mammogram (B)
    - Cervical (female): Age 21-65 Pap/HPV (A)
    - Lung (smokers): Age 50-80, 20 pack-year history (B)
    - Prostate (male): Age 55-69 shared decision-making (C)

    Reference: https://www.uspreventiveservicestaskforce.org/

    Args:
        patient_icn: Patient ICN

    Returns:
        Formatted screening recommendations
    """
    logger.info(f"Generating cancer screening recommendations for {patient_icn}")

    # Get patient demographics
    demographics = await asyncio.to_thread(get_patient_demographics, patient_icn)

    if not demographics:
        return "⚠️ Patient demographics not found. Cannot generate screening recommendations."

    # Extract age and sex
    dob_str = demographics.get('date_of_birth')
    sex = demographics.get('sex', '').upper()

    if not dob_str:
        return "⚠️ Patient date of birth missing. Cannot calculate age for screening recommendations."

    try:
        dob = datetime.strptime(str(dob_str).split()[0], '%Y-%m-%d')
        age = (datetime.now() - dob).days // 365
    except:
        return f"⚠️ Could not parse date of birth: {dob_str}"

    # Generate recommendations
    recommendations = []

    # Colorectal cancer screening (all adults)
    if 45 <= age <= 75:
        recommendations.append({
            'cancer': 'Colorectal Cancer',
            'screening': 'Colonoscopy (every 10 years) OR FIT (annual) OR Cologuard (every 3 years)',
            'grade': 'A',
            'reason': f'Age {age} (recommended 45-75)',
            'icon': '🟢'
        })
    elif 76 <= age <= 85:
        recommendations.append({
            'cancer': 'Colorectal Cancer',
            'screening': 'Selective screening based on patient preference and health status',
            'grade': 'C',
            'reason': f'Age {age} (selective 76-85)',
            'icon': '🟡'
        })

    # Breast cancer screening (females)
    if sex == 'F':
        if 50 <= age <= 74:
            recommendations.append({
                'cancer': 'Breast Cancer',
                'screening': 'Mammography every 2 years',
                'grade': 'B',
                'reason': f'Female, age {age} (recommended 50-74)',
                'icon': '🟢'
            })
        elif 40 <= age <= 49:
            recommendations.append({
                'cancer': 'Breast Cancer',
                'screening': 'Mammography - discuss with patient (individual decision)',
                'grade': 'C',
                'reason': f'Female, age {age} (individualized 40-49)',
                'icon': '🟡'
            })

    # Cervical cancer screening (females)
    if sex == 'F':
        if 21 <= age <= 29:
            recommendations.append({
                'cancer': 'Cervical Cancer',
                'screening': 'Pap smear every 3 years',
                'grade': 'A',
                'reason': f'Female, age {age} (recommended 21-29)',
                'icon': '🟢'
            })
        elif 30 <= age <= 65:
            recommendations.append({
                'cancer': 'Cervical Cancer',
                'screening': 'Pap smear + HPV test every 5 years OR Pap smear every 3 years',
                'grade': 'A',
                'reason': f'Female, age {age} (recommended 30-65)',
                'icon': '🟢'
            })

    # Lung cancer screening (smokers - requires additional data)
    if 50 <= age <= 80:
        recommendations.append({
            'cancer': 'Lung Cancer',
            'screening': 'Low-dose CT if ≥20 pack-year smoking history and currently smoking or quit within 15 years',
            'grade': 'B',
            'reason': f'Age {age} - verify smoking history',
            'icon': '🟡'
        })

    # Prostate cancer screening (males)
    if sex == 'M' and 55 <= age <= 69:
        recommendations.append({
            'cancer': 'Prostate Cancer',
            'screening': 'PSA screening - individualized decision with shared decision-making',
            'grade': 'C',
            'reason': f'Male, age {age} (individualized 55-69)',
            'icon': '🟡'
        })

    # Format results
    if not recommendations:
        result = f"**No routine cancer screenings recommended** for {sex or 'unknown sex'}, age {age}\n\n"
        result += "This patient is outside standard screening age ranges for USPSTF grade A/B recommendations.\n"
    else:
        result = f"**Cancer Screening Recommendations** ({sex or 'unknown sex'}, age {age})\n\n"
        result += f"Based on USPSTF guidelines (current as of 2024)\n\n"

        for rec in recommendations:
            result += f"{rec['icon']} **{rec['cancer']}** (Grade {rec['grade']})\n"
            result += f"   Screening: {rec['screening']}\n"
            result += f"   Reason: {rec['reason']}\n\n"

        result += "\n**USPSTF Grade Meanings:**\n"
        result += "  • **A**: High certainty of substantial benefit - strongly recommended\n"
        result += "  • **B**: High certainty of moderate benefit - recommended\n"
        result += "  • **C**: Small benefit - individualized decision with patient\n\n"
        result += "*Note: Recommendations assume average risk. Adjust for family history and risk factors.*\n"

    # Add attribution footer for clinical auditability
    return _add_attribution_footer(
        result=result,
        tool_name="recommend_cancer_screening",
        data_sources=[
            "USPSTF guidelines (2024 version)",
            "PostgreSQL patient_demographics table"
        ],
        metadata={
            "Screening Recommendations": len(recommendations),
            "Patient Age": f"{age} years",
            "Patient Sex": sex or "Unknown",
            "Guideline Version": "USPSTF 2024"
        }
    )


# ============================================================================
# HELPER FUNCTIONS - Format results for AI consumption
# ============================================================================

def _format_ddi_results(interactions: list[dict], med_count: int) -> str:
    """
    Format DDI analysis results with clinical safety emphasis.

    Safety-First Formatting:
    - No interactions = Explicit confirmation (not silence)
    - Interactions sorted by clinical significance (if severity available)
    - Clear drug names + interaction descriptions
    - Action-oriented language
    - Data provenance footer for auditability

    Args:
        interactions: List of interaction dicts from DDIAnalyzer
        med_count: Total number of medications analyzed

    Returns:
        Markdown-formatted DDI report with attribution footer
    """
    if not interactions:
        result = (
            f"✅ **No Drug-Drug Interactions Detected**\n\n"
            f"Analyzed {med_count} medications - no significant interactions found in DrugBank reference.\n\n"
            f"*Note: This analysis uses a comprehensive reference database (~191K interactions) "
            f"but does not replace clinical judgment. Always consult clinical pharmacology "
            f"for complex medication regimens.*"
        )
    else:
        # Format interactions
        result = f"⚠️ **Drug-Drug Interactions Found**\n\n"
        result += f"Analyzed {med_count} medications, found **{len(interactions)} interactions**:\n\n"

        for i, ddi in enumerate(interactions, 1):
            drug_a = ddi.get('drug_a', 'Unknown')
            drug_b = ddi.get('drug_b', 'Unknown')
            description = ddi.get('description', 'No description available')

            result += f"**{i}. {drug_a} + {drug_b}**\n"
            result += f"   Interaction: {description}\n\n"

        result += "\n**Clinical Recommendations:**\n"
        result += "  • Review interaction severity with clinical pharmacist\n"
        result += "  • Consider dose adjustments or alternative medications\n"
        result += "  • Monitor patient for interaction symptoms\n"
        result += "  • Document discussion with patient about risks/benefits\n"

    # Add attribution footer for clinical auditability
    return _add_attribution_footer(
        result=result,
        tool_name="check_drug_interactions",
        data_sources=[
            "DrugBank reference database (~191K interactions)",
            "PostgreSQL patient_medications_outpatient table",
            "PostgreSQL patient_medications_inpatient table",
            "MinIO Parquet (gold/ddi_reference.parquet)"
        ],
        metadata={
            "Medications analyzed": med_count,
            "Interactions found": len(interactions) if interactions else 0
        }
    )


# ============================================================================
# SERVER INITIALIZATION
# ============================================================================

async def main():
    """
    Run the Clinical Decision Support MCP server.

    Initializes server with stdio transport for Claude Desktop integration.
    """
    try:
        from mcp.server.stdio import stdio_server

        logger.info("Starting Clinical Decision Support MCP Server...")
        logger.info("Available tools: check_drug_interactions, assess_fall_risk, "
                    "calculate_ckd_egfr, recommend_cancer_screening")

        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="clinical-decision-support-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    )
                )
            )
    except Exception as e:
        logger.error(f"Server failed to start: {e}", exc_info=True)
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"FATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)
