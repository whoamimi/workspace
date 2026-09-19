
# WORKSPACE DIR
from pathlib import Path

INPUT_DIR = Path("/kaggle/input")
INPUT_PATH = INPUT_DIR / "forecasting-the-future-the-helios-corn-climate-challenge"
OUTPUT_DIR = Path("/kaggle/working")
OUTPUT_PATH = OUTPUT_DIR / "submission.csv"

class ClimateLabels:
    """ Climate Weather Feature Signals output from model and not the actual or true values during the insighted event. """
    heat_stress = ['climate_risk_cnt_locations_heat_stress_risk_low','climate_risk_cnt_locations_heat_stress_risk_medium','climate_risk_cnt_locations_heat_stress_risk_high']
    cold_stress = ['climate_risk_cnt_locations_unseasonably_cold_risk_low', 'climate_risk_cnt_locations_unseasonably_cold_risk_medium','climate_risk_cnt_locations_unseasonably_cold_risk_high']
    precip_stress = ['climate_risk_cnt_locations_excess_precip_risk_low','climate_risk_cnt_locations_excess_precip_risk_medium',
    'climate_risk_cnt_locations_excess_precip_risk_high']
    drought_stress = ['climate_risk_cnt_locations_drought_risk_low', 'climate_risk_cnt_locations_drought_risk_medium','climate_risk_cnt_locations_drought_risk_high']
    columns = heat_stress + cold_stress + precip_stress + drought_stress
    extreme_signals = [
        'climate_risk_cnt_locations_heat_stress_risk_high',
        'climate_risk_cnt_locations_unseasonably_cold_risk_high',
        'climate_risk_cnt_locations_excess_precip_risk_high',
        'climate_risk_cnt_locations_drought_risk_high',
    ]
    medium_signals = [
        'climate_risk_cnt_locations_heat_stress_risk_medium',
        'climate_risk_cnt_locations_unseasonably_cold_risk_medium',
        'climate_risk_cnt_locations_excess_precip_risk_medium',
        'climate_risk_cnt_locations_drought_risk_medium',
    ]
    low_signals = [
        'climate_risk_cnt_locations_heat_stress_risk_low',
        'climate_risk_cnt_locations_unseasonably_cold_risk_low',
        'climate_risk_cnt_locations_excess_precip_risk_low',
        'climate_risk_cnt_locations_drought_risk_low',
    ]

class FutureLabels:
    # Commodity Furture Pricing Signals
    # C=Corn, W=Wheat, S=Soybean
    # 1=FRONT MONTH FUTURES, 2=2ND MONTH FUTURES
    # Closing price in the front month wrt commodity type
    front_month_prices = ['futures_close_ZC_1', 'futures_close_ZW_1', 'futures_close_ZS_1']
    # Closing price in the second month wrt commodity type
    second_month_prices = ['futures_close_ZC_2']
    # Daily percentage / logs return for corn front-month
    daily_returns = ['futures_zc1_ret_pct', 'futures_zc1_ret_log']
    # Price diff / ratio of 2nd to front months
    spread_returns = ['futures_zc_term_spread', 'futures_zc_term_ratio']
    # Moving Averages wrt suffix days
    ma_measures = ['futures_zc1_ma_20', 'futures_zc1_ma_60', 'futures_zc1_ma_120']
    # Volatility wrt suffix days
    vol_measures = ['futures_zc1_vol_20', 'futures_zc1_vol_60']

    measures = ma_measures + vol_measures
    close_prices = front_month_prices + second_month_prices
    columns = close_prices + daily_returns + spread_returns + ma_measures + vol_measures
    # extra
    cross_relations = [
        'futures_zw_zc_spread',
        'futures_zc_zw_ratio',
        'futures_zs_zc_spread',
        'futures_zc_zs_ratio'
    ]

class MetaLabels:
    identifiers = [
        'ID',
        'crop_name',
        'country_name',
        'country_code',
        'region_name',
        'region_id',
    ]
    temporal = ["harvest_period" "growing_season_year", "date_on"]
    columns = identifiers + temporal
    extra = ['date_on_year', 'date_on_month', 'date_on_year_month']

# ALL FUTURE (MAIN) DATASET COLUMNS
FT_COLS = MetaLabels.columns + MetaLabels.extra
# ALL MARKET SHARE DATA COLUMNS
MT_COLS = [
    'country_name',
    'country_code',
    'region_name',
    'region_id',
    # key value
    'percent_country_production'
]

# UNUSED COLUMNS TO DROP BEFORE TRAINING
DROP_COLS = ["crop_name"]

# COLUMNS REQUIRED TO BE PRESENT IN SUBMISSION OUTPUT
SUBMISSION_COLS = [
    "date_on",
    "country_name",
    "region_name"
]

list(INPUT_PATH.glob("*.csv"))