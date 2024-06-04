import pandas as pd
from mlops.homework_03.utils.prepare import prepare_data

if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(data: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
    """
    Args:
        data: The output from the ingest block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        pd.DataFrame: the processed data
    """
    df = prepare_data(data)
    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
