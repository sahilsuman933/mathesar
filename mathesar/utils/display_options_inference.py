import json

from thefuzz import fuzz

from db.columns.operations.select import get_column_attnum_from_name
from db.types import base
from db.types.base import get_qualified_name
from db.types.money import get_first_money_array_with_symbol

MATHESAR_MONEY = get_qualified_name(base.MathesarCustomType.MATHESAR_MONEY.value)


def infer_mathesar_money_display_options(table_oid, engine, column_attnum):
    money_array = get_first_money_array_with_symbol(table_oid, engine, column_attnum)
    if money_array is None:
        return None
    else:
        with open("currency_info.json", 'r') as currency_file:
            currency_dict = json.loads(currency_file.read())
            greatest_currency_similarity_score = 10  # Threshold score
            selected_currency_code = None
            for currency_code, currency_details in currency_dict.items():
                currency_similarity_score = fuzz.ratio(currency_details['currency_symbol'], money_array[3])
                if currency_similarity_score == 100:
                    return {'currency_code': currency_code}
                elif currency_similarity_score > greatest_currency_similarity_score:
                    greatest_currency_similarity_score = currency_similarity_score
                    selected_currency_code = currency_code
            if selected_currency_code is not None:
                return {'currency_code': currency_code}
            else:
                # TODO Improve default values based on locale
                return {
                    'decimal_symbol': money_array[2] if money_array[2] is not None else ".",
                    'digit_grouping_symbol': money_array[1] if money_array[1] is not None else ",",
                    'symbol': money_array[3],
                    'symbol_location': 1,
                    'digit_grouping': []
                }


def infer_table_column_display_options(table, col_name_type_dict):
    inferred_display_options = {}
    for column_name, columnn_type in col_name_type_dict.items():
        inference_fn = display_options_inference_map.get(columnn_type.lower())
        if inference_fn is not None:
            column_attnum = get_column_attnum_from_name(table.oid, column_name, table.schema._sa_engine)
            inferred_display_options[column_name] = inference_fn(table.oid, table.schema._sa_engine, column_attnum)
        else:
            inferred_display_options[column_name] = None
    return inferred_display_options


display_options_inference_map = {
    MATHESAR_MONEY: infer_mathesar_money_display_options
}
