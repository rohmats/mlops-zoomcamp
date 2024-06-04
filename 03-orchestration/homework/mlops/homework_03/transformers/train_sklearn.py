import pandas as pd
from sklearn.linear_model import LinearRegression

if "transformer" not in globals():
    from mage_ai.data_preparation.decorators import transformer
if "test" not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def fit_linear_regression(data, *args, **kwargs):
    """

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Tuple: LinearRegression model and DictVectorizer
    """
    # Specify your transformation logic here
    X, y, dv = data["training_set_export"]
    lr = LinearRegression()
    lr.fit(X, y)
    print(f"The intercept for the fitted model is {lr.intercept_}")
    return lr, dv


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "The output is undefined"
