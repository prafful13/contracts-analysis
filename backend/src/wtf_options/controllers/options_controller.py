from flask import Blueprint, request, jsonify
from ..services.options_service import analyze_income_options, analyze_buy_options
import logging

options_blueprint = Blueprint('options', __name__)

logger = logging.getLogger(__name__)

@options_blueprint.route('/analyze', methods=['POST'])
def analyze_options_route():
    """
    API endpoint to analyze options based on frontend parameters.
    Routes to different analysis functions based on 'screenerType'.
    """
    params = request.json
    screener_type = params.get('screenerType', 'income')
    logger.info(f"Received request for screenerType: {screener_type}")
    logger.debug(f"Request params: {params}")

    if screener_type == 'buy':
        results = analyze_buy_options(params)
    else:
        results = analyze_income_options(params)
    logger.info(f"Results: {jsonify(results)}")
    return jsonify(results)
