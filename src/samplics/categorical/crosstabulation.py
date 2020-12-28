"""Cross-tabulation module 

The module implements the cross-tabulation analysis.

"""


from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from scipy.stats import t as student
from scipy.stats.stats import f_oneway

from samplics.utils.formats import numpy_array, remove_nans
from samplics.utils.types import Array, Number, StringNumber

from samplics.estimation import TaylorEstimator


class CrossTabulation:
    """provides methods for analyzing cross-tabulations"""

    def __init__(self, table_type: str, alpha: float = 0.05) -> None:
        """[summary]

        Args:
            table (str): [description]
        """

        if table_type.lower() not in ("oneway", "twoway"):
            raise ValueError("table parameter must take values 'oneway' or 'twoway'!")

        self.table_type = table_type.lower()
        self.table = Dict[StringNumber, StringNumber]
        self.stats = Dict[str, Number]
        # self.design = Dict[str, Number]
        self.alpha = alpha

    def _oneway(
        self,
        row_var: Array,
        samp_weight: Array,
        stratum: Optional[Array] = None,
        psu: Optional[Array] = None,
        ssu: Optional[Array] = None,
        fpc: Union[Dict, float] = 1,
    ) -> None:

        levels, counts = np.unique(row_var, return_counts=True)

        tbl_estimator = TaylorEstimator(parameter="total", alpha=self.alpha)
        tbl_estimator.estimate(
            y=np.ones(row_var.shape[0]),
            samp_weight=samp_weight,
            stratum=stratum,
            psu=psu,
            ssu=ssu,
            domain=row_var,
        )

    def _twoway():
        pass

    def tabulate(
        self,
        cat_vars: Array,
        samp_weight: Array,
        stratum: Optional[Array] = None,
        psu: Optional[Array] = None,
        ssu: Optional[Array] = None,
        fpc: Union[Dict, float] = 1,
        remove_nan: bool = False,
    ) -> None:

        cat_vars = numpy_array(cat_vars)

        if self.table_type == "oneway" and cat_vars.shape[0] > 1:
            raise AssertionError("")

        samp_weight = numpy_array(samp_weight)
        if stratum is not None:
            stratum = numpy_array(stratum)
        if psu is not None:
            psu = numpy_array(psu)
        if ssu is not None:
            ssu = numpy_array(ssu)
        if fpc is not None:
            fpc = numpy_array(fpc)

        if remove_nan:
            excluded_units = np.isnan(samp_weight)
            samp_weight, stratum, psu, ssu, fpc = remove_nans(
                excluded_units, samp_weight, stratum, psu, ssu, fpc
            )

        if self.table_type == "oneway":
            self._oneway()
        elif self.table_type == "twoway":
            self._twoway()
        else:
            raise ValueError("Parameter 'table_type' is not valid!")