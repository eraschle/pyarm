from typing import Dict, Iterable

import pandas as pd

from pyarm.factories.parameter import ParameterDefinition
from pyarm.factories import parameter_definition as pardef


def _combine_dataframes(dataframes: Iterable) -> pd.DataFrame:
    """
    Combines the dataframes into one dataframe.
    """
    return pd.concat(dataframes, ignore_index=True)


def get_custom_definitions(dfa_data: Dict[str, pd.DataFrame]) -> Dict[str, ParameterDefinition]:
    """
    Evaluate the data and perform any necessary transformations.
    """
    combined_data = _combine_dataframes(dfa_data.values())
    custom_definitions = {}
    for column in combined_data.columns:
        values = combined_data[column].dropna().unique()
        definition = pardef.get_definition(column, values)
        custom_definitions[column] = definition
    return custom_definitions
