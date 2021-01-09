"""Sampling selection module

The module has one main class called *SampleSelection* which provides a number of random selection methodsand associated probability of selection. All the samping techniques implemented in this 
modules are discussed in the following reference book: Cochran, W.G. (1977) [#c1977]_, 
Kish, L. (1965) [#k1965]_, and Lohr, S.L. (2010) [#l2010]_. Furthermore, Brewer, K.R.W. and 
Hanif, M. (1983) [#bh1983]_ provides comprehensive and detailed descriptions of these complex 
sampling algorithms.

.. [#c1977] Cochran, W.G. (1977), *Sampling Techniques, 3rd edn.*, Jonh Wiley & Sons, Inc.
.. [#k1965] Kish, L. (1965), *Survey Sampling*, Jonh Wiley & Sons, Inc.
.. [#l2010] Lohr, S.L. (2010), *Sampling: Design and Analysis, 2nd edn.*, Cengage Learning, Inc.
.. [#bh1983] Brewer, K.R.W. and Hanif, M. (1983), *Sampling With Unequal Probabilities*,  
   Springer-Verlag New York, Inc
"""

from ast import Str
from typing import Dict, Generic, Tuple, Union, Optional, overload

import numpy as np
import pandas as pd

import math

from samplics.utils import formats
from samplics.utils.types import Array, Number, Series, StringNumber


class SampleSelection(Generic[Number, StringNumber]):
    """*SampleSelection* implements a number of sampling selection algorithms.

    The implemented sampling algorithms are the simple random sampling (srs), the
    systematic selection (sys), five different algorithms of probability proportional
    to size (pps), and the generic selection based on probabilities of selection.

    Attributes of the class:
        | method (str): a string specifying the sampling algorithm. The available
        |   sampling algorithms are: simple random sampling (srs), systematic selection (sys),
        |   Brewer's procedure (pps-brewer), Hanurav-Vijayan procedure (pps-hv),
        |   Murphy's procedure (pps-murphy), Rao-Sampford procedure (pps-rs), systematic
        |   pps (pps-sys), and a generic selection from arbitrary probabilities using
        |   *numpy.random.choice()* method.
        | stratification (bool): indicates if the sampling procedure is stratified or not.
        | with_replacement (bool): indicates whether the selection is with replacement.

    Main functions:
        | inclusion_probs(): provides the inclusion probabilities.
        | joNumber_inclusion_probs(): provides the joNumber probalities of selection.
        | select(): indicates the selected sample.

    TODO: handling of certaNumberies and implementation of joNumber_inclusion_probs().
    """

    def __init__(
        self,
        method,
        stratification=False,
        with_replacement=True,
    ):
        if method.lower() in (
            "srs",
            "sys",
            "pps-brewer",
            "pps-hv",  # Hanurav-Vijayan
            "pps-murphy",
            "pps-rs",
            "pps-sys",
            "grs",
        ):
            self.method = method.lower()  # grs for generic random selection
        else:
            raise ValueError(
                "method must be in ('srs', 'sys', 'pps-brewer', 'pps-hv', 'pps-murphy', 'pps-rs, 'pps-sys', 'grs')"
            )
        self.stratification = True if stratification else False
        self.with_replacement = with_replacement
        self.fpc = {}

    @staticmethod
    def _to_dataframe(
        samp_unit,
        stratum,
        mos,
        sample,
        hits,
        probs,
    ) -> pd.DataFrame:

        df = pd.DataFrame(
            {
                "_samp_unit": samp_unit,
                "_stratum": stratum,
                "_mos": mos,
                "_sample": sample,
                "_hits": hits,
                "_probs": probs,
            }
        )

        if stratum is None:
            df.drop(columns=["_stratum"], inplace=True)
        if mos is None:
            df.drop(columns=["_mos"], inplace=True)

        return df

    def _calculate_fpc(
        self,
        samp_unit,
        samp_size,
        stratum,
    ):

        samp_unit = formats.sample_units(samp_unit, unique=True)
        samp_size = formats.sample_size_dict(samp_size, self.stratification, stratum)

        if isinstance(samp_size, dict):
            self.fpc = dict()
            strata = np.unique(stratum)
            for k, s in enumerate(strata):
                number_units_s = len(samp_unit[stratum == s])
                self.fpc[s] = np.sqrt((number_units_s - samp_size[s]) / (number_units_s - 1))
        else:
            self.fpc = np.sqrt((samp_unit.size - samp_size) / (samp_unit.size - 1))

    def _grs_select(
        self,
        probs,
        samp_unit,
        samp_size,
        stratum=None,
    ):

        samp_size = formats.sample_size_dict(samp_size, self.stratification, stratum)
        sample = hits = np.zeros(samp_unit.size).astype(int)
        self._calculate_fpc(samp_unit, samp_size, stratum)
        if isinstance(samp_size, dict):
            all_indices = np.array(range(samp_unit.size))
            sampled_indices_list = []
            for s in np.unique(stratum):
                stratum_units = stratum == s
                probs_s = probs[stratum_units] / np.sum(probs[stratum_units])
                sampled_indices_s = np.random.choice(
                    all_indices[stratum_units],
                    samp_size[s],
                    self.with_replacement,
                    probs_s,
                )
                sampled_indices_list.append(sampled_indices_s)
            sampled_indices = np.array(
                [val for sublist in sampled_indices_list for val in sublist]
            ).flatten()
        else:
            sampled_indices = np.random.choice(
                samp_unit.size,
                samp_size,
                self.with_replacement,
                probs / np.sum(probs),
            )

        indices_s, hits_s = np.unique(sampled_indices, return_counts=True)
        sample[indices_s] = True
        hits[indices_s] = hits_s

        return sample, hits

    @staticmethod
    def _anycertaNumbery(
        samp_size,
        stratum,
        mos,
    ) -> bool:

        if stratum is not None:
            probs = np.zeros(stratum.size)
            for s in np.unique(stratum):
                stratum_units = stratum == s
                mos_s = mos[stratum_units]
                probs[stratum_units] = samp_size[s] * mos_s / np.sum(mos_s)
        else:
            probs = samp_size * mos / np.sum(mos)

        certaNumbery = (probs >= 1).any()

        return certaNumbery

    # SRS methods
    def _srs_inclusion_probs(
        self,
        samp_unit,
        samp_size,
        stratum=None,
    ) -> np.ndarray:

        samp_unit = formats.sample_units(samp_unit)
        samp_size = formats.sample_size_dict(samp_size, self.stratification, stratum)

        number_units = samp_unit.size
        if isinstance(samp_size, dict):
            incl_probs = np.zeros(number_units) * np.nan
            for s in np.unique(stratum):
                number_units_s = samp_unit[stratum == s].size
                incl_probs[stratum == s] = samp_size[s] / number_units_s
        else:
            number_units = samp_unit.size
            incl_probs = np.ones(number_units) * samp_size / number_units

        return incl_probs

    # PPS methods
    def _pps_inclusion_probs(
        self,
        samp_unit,
        samp_size,
        mos,
        stratum=None,
    ) -> np.ndarray:

        samp_unit = formats.sample_units(samp_unit, unique=True)
        samp_size = formats.sample_size_dict(samp_size, self.stratification, stratum)

        if isinstance(samp_size, dict):
            number_units = samp_unit.size
            incl_probs = np.zeros(number_units) * np.nan
            for s in np.unique(stratum):
                stratum_units = stratum == s
                mos_s = mos[stratum_units]
                incl_probs[stratum_units] = samp_size[s] * mos_s / np.sum(mos_s)
        else:
            incl_probs = samp_size * mos / np.sum(mos)

        return incl_probs

    @staticmethod
    def _pps_sys_select(samp_unit, samp_size, mos):

        cumsize = np.append(0, np.cumsum(mos))
        samp_Numbererval = cumsize[-1] / samp_size
        random_start = np.random.random_sample() * samp_Numbererval
        random_picks = random_start + samp_Numbererval * np.linspace(0, samp_size - 1, samp_size)

        hits = np.zeros(samp_unit.size).astype(int)
        for k in range(cumsize.size - 1):
            for ll in range(random_picks.size):
                if cumsize[k] < random_picks[ll] <= cumsize[k + 1]:
                    hits[k] += 1

        return hits >= 1, hits

    @staticmethod
    def _pps_hv_select(samp_unit, samp_size, mos):

        pop_size = samp_unit.size
        all_indices = np.arange(pop_size)
        size_order = mos.argsort()
        all_indices_sorted = all_indices[size_order]
        mos_sorted = mos[size_order]
        probs_sorted = np.append(mos_sorted / np.sum(mos_sorted), 1 / samp_size)
        last_nplus1_probs = probs_sorted[range(-(samp_size + 1), 0)]
        diff_probs = np.ediff1d(last_nplus1_probs)
        s = np.sum(probs_sorted[0 : (pop_size - samp_size)])
        initial_probs_selection = (
            samp_size
            * diff_probs
            * (1 + np.linspace(1, samp_size, samp_size) * probs_sorted[pop_size - samp_size] / s)
        )
        probs_sorted = np.delete(probs_sorted, -1)
        selected_i = np.random.choice(np.arange(0, samp_size), size=1, p=initial_probs_selection)[
            0
        ]
        sampled_indices = all_indices_sorted[selected_i + 1 : samp_size]

        notsampled_indices = np.delete(all_indices_sorted, sampled_indices)
        notsampled_probs = np.delete(probs_sorted, sampled_indices)
        p_denominator = (
            s
            + np.linspace(
                1,
                pop_size - samp_size + selected_i + 1,
                pop_size - samp_size + selected_i + 1,
            )
            * probs_sorted[pop_size - samp_size]
        )
        p_starts = notsampled_probs / p_denominator
        range_part2 = range(pop_size - samp_size, pop_size - samp_size + selected_i)
        p_starts[range_part2] = probs_sorted[pop_size - samp_size] / p_denominator[range_part2]
        p_starts_sum = np.cumsum(np.flip(p_starts)[range(p_starts.size - 1)])
        p_starts_sum = np.append(np.flip(p_starts_sum), 1)
        p_double_starts = p_starts / p_starts_sum
        p_double_starts[-1] = 0

        start_j = 0
        end_j = pop_size - samp_size + 1
        for ll in np.arange(selected_i + 1):
            sampling_space = range(start_j, end_j)
            p_double_space = p_double_starts[range(start_j, end_j)]
            p_double_space = 1 - (selected_i + 1 - ll) * np.append(0, p_double_space)
            p_double_space = np.delete(p_double_space, -1)
            a_j = (
                (samp_size - ll + 1) * p_starts[range(start_j, end_j)] * np.cumprod(p_double_space)
            )
            indice_j = np.random.choice(sampling_space, size=1, p=a_j / np.sum(a_j))[0]
            selected_j = notsampled_indices[indice_j]
            sampled_indices = np.append(sampled_indices, selected_j)
            start_j = indice_j + 1
            end_j += 1
        sample = hits = np.zeros(samp_unit.size).astype(int)
        sample[sampled_indices] = True
        hits[sampled_indices] = 1

        return sample, hits

    @staticmethod
    def _pps_brewer_select(samp_unit, samp_size, mos):

        all_indices = np.arange(samp_unit.size)
        all_probs = mos / np.sum(mos)
        working_probs = all_probs * (1 - all_probs) / (1 - samp_size * all_probs)
        working_probs = working_probs / np.sum(working_probs)
        sampled_indices = np.random.choice(all_indices, 1, p=working_probs)
        sample = hits = np.zeros(samp_unit.size).astype(int)
        for s in np.arange(1, samp_size):
            remaining_indices = np.delete(all_indices, sampled_indices)
            remaining_probs = np.delete(all_probs, sampled_indices)
            remaining_probs = (
                remaining_probs * (1 - remaining_probs) / (1 - (samp_size - s) * remaining_probs)
            )
            remaining_probs = remaining_probs / sum(remaining_probs)
            current_selection = np.random.choice(remaining_indices, 1, p=remaining_probs)
            sampled_indices = np.append(sampled_indices, current_selection)

        sample[sampled_indices] = True
        hits[sampled_indices] = 1

        return sample, hits

    @staticmethod
    def _pps_murphy_select(samp_unit, samp_size, mos):

        if samp_size != 2:
            raise ValueError(
                "For the Murphy's selection algorithm, sample size must be equal to 2"
            )
        all_indices = np.arange(samp_unit.size)
        all_probs = mos / np.sum(mos)
        sampled_indices = np.random.choice(all_indices, 1, p=all_probs)
        remaining_indices = np.delete(all_indices, sampled_indices)
        remaining_probs = np.delete(all_probs, sampled_indices)
        remaining_probs = remaining_probs / (1 - all_probs[sampled_indices])
        current_selection = np.random.choice(remaining_indices, 1, p=remaining_probs)
        sampled_indices = np.append(sampled_indices, current_selection)

        sample = hits = np.zeros(samp_unit.size).astype(int)
        sample[sampled_indices] = True
        hits[sampled_indices] = 1

        return sample, hits

    @staticmethod
    def _pps_rs_select(samp_unit, samp_size, mos: Array) -> Tuple[Array, Array]:

        all_indices = np.arange(samp_unit.shape[0])
        all_probs = mos / np.sum(mos)

        stop = False
        sample = hits = np.zeros(samp_unit.shape[0]).astype(int)
        sampled_indices = None
        while stop is not True:
            sampled_indices = np.random.choice(all_indices, 1, p=all_probs)
            remaining_indices = np.delete(all_indices, sampled_indices)
            remaining_probs = all_probs / (1 - samp_size * all_probs)
            remaining_probs = np.delete(remaining_probs, sampled_indices)
            remaining_probs = remaining_probs / np.sum(remaining_probs)
            remaining_sample = np.random.choice(
                remaining_indices, samp_size - 1, p=remaining_probs
            )
            _, counts = np.unique(np.append(sampled_indices, remaining_sample), return_counts=True)
            if (counts == 1).all():
                stop = True

        sample[sampled_indices] = True
        hits[sampled_indices] = 1

        return sample, hits

    def _pps_select(
        self,
        samp_unit,
        samp_size,
        stratum,
        mos,
    ):

        samp_unit = formats.sample_units(samp_unit, unique=True)
        samp_size = formats.sample_size_dict(samp_size, self.stratification, stratum)

        sample = hits = np.zeros(samp_unit.size).astype(int)
        if isinstance(samp_size, dict):
            for s in np.unique(stratum):
                stratum_units = stratum == s
                if self.method in "pps-sys":  # systematic
                    (sample[stratum_units], hits[stratum_units],) = self._pps_sys_select(
                        samp_unit[stratum_units],
                        samp_size[s],
                        mos[stratum_units],
                    )
                elif self.method in "pps-hv":  # "hanurav-vijayan"
                    (sample[stratum_units], hits[stratum_units],) = self._pps_hv_select(
                        samp_unit[stratum_units],
                        samp_size[s],
                        mos[stratum_units],
                    )
                elif self.method in "pps-brewer":
                    (sample[stratum_units], hits[stratum_units],) = self._pps_brewer_select(
                        samp_unit[stratum_units],
                        samp_size[s],
                        mos[stratum_units],
                    )
                elif self.method in "pps-murphy":
                    (sample[stratum_units], hits[stratum_units],) = self._pps_murphy_select(
                        samp_unit[stratum_units],
                        samp_size[s],
                        mos[stratum_units],
                    )
                elif self.method in "pps-rs":
                    (sample[stratum_units], hits[stratum_units],) = self._pps_rs_select(
                        samp_unit[stratum_units],
                        samp_size[s],
                        mos[stratum_units],
                    )
        else:
            if self.method in "pps-sys":  # systematic
                sample, hits = self._pps_sys_select(samp_unit, samp_size, mos)
            elif self.method in "pps-hv":  # "hanurav-vijayan"
                sample, hits = self._pps_hv_select(samp_unit, samp_size, mos)
            elif self.method in "pps-brewer":
                sample, hits = self._pps_brewer_select(samp_unit, samp_size, mos)
            elif self.method in "pps-murphy":
                sample, hits = self._pps_murphy_select(samp_unit, samp_size, mos)
            elif self.method in "pps-rs":
                sample, hits = self._pps_rs_select(samp_unit, samp_size, mos)

        return sample, hits

    # SYSTEMATIC methods

    def _sys_inclusion_probs(
        self,
        samp_unit,
        samp_size: Optional[Dict[StringNumber, Number]] = None,
        stratum=None,
        samp_rate: Optional[Dict[StringNumber, Number]] = None,
    ) -> np.ndarray:

        pass

    @staticmethod
    def _sys_selection_method(samp_unit, samp_size, samp_rate):

        if samp_size is not None and samp_rate is not None:
            raise AssertionError(
                "Both samp_size and samp_rate are provided. Only one of the two parameters should be specified."
            )

        if samp_rate is not None:
            samp_size = math.floor(samp_rate * samp_unit.size)
        samp_Numbererval = math.floor(samp_unit.size / samp_size)  # same as 1 / samp_rate
        random_start = np.random.choice(range(0, samp_Numbererval))
        random_picks = random_start + samp_Numbererval * np.linspace(
            0, samp_size - 1, samp_size
        ).astype(int)
        hits = np.zeros(samp_unit.size).astype(int)
        hits[random_picks] = 1

        return hits == 1, hits

    def _sys_select(
        self,
        samp_unit,
        samp_size,
        stratum,
        samp_rate,
    ):

        sample = hits = np.zeros(samp_unit.size).astype(int)
        if self.stratification:
            for s in np.unique(stratum):
                samp_size_s = None if samp_size is None else samp_size[s]
                samp_rate_s = None if samp_rate is None else samp_rate[s]
                stratum_units = stratum == s
                (
                    sample[stratum_units],
                    hits[stratum_units],
                ) = self._sys_selection_method(samp_unit[stratum_units], samp_size_s, samp_rate_s)
        else:
            samp_size_n = None if samp_size is None else samp_size
            samp_rate_n = None if samp_rate is None else samp_rate
            sample, hits = self._sys_selection_method(samp_unit, samp_size_n, samp_rate_n)

        return sample, hits

    # public methods

    def inclusion_probs(
        self,
        samp_unit,
        samp_size=None,
        stratum=None,
        mos=None,
        samp_rate=None,
    ) -> np.ndarray:
        """Computes the inclusion probabilities according to the sampling scheme.

        Args:
            samp_unit (Array): an array of all the observations in the target population.
            samp_size (Union[Dict[Any, Number], Number, None], optional): the dictionary of sample
            sizes by stratum, if applicable. Defaults to None.
            stratum (Optional[Array], optional): array of the strata associated to the
                population units. Defaults to None.
            mos (Optional[Array], optional): array of the measure of size associated to the
                population units. Defaults to None.
            samp_rate (Union[Dict[Any, Number], Number, None], optional): sampling rate provided
                by stratum if applicable. Defaults to None.

        Raises:
            AssertionError: raises an assertion error if some of the clusters are certaNumberies.

        Returns:
            np.ndarray: an array of the probabilities of inclusion.
        """
        if samp_size is not None and samp_rate is not None:
            raise AssertionError(
                "Both samp_size and samp_rate are provided. Only one of the two parameters should be specified."
            )

        if self.stratification and stratum is None:
            raise AssertionError("Stratum must be provided for stratified samples!")

        samp_unit = formats.sample_units(samp_unit, unique=True)

        if stratum is not None:
            stratum = formats.numpy_array(stratum)
            if isinstance(samp_size, (int, float)):
                strata = np.unique(stratum)
                samp_size_temp = dict(zip(strata, np.repeat(samp_size, strata.shape[0])))
            # elif isinstance(samp_rate, Number):
            #     strata = np.unique(stratum)
            #     samp_rate_temp = dict(zip(strata, np.repeat(samp_rate, strata.shape[0])))
            elif isinstance(samp_size, dict):
                samp_size_temp = samp_size.copy()
            else:
                raise TypeError("samp_size or samp_rate has the wrong type")
        else:
            if isinstance(samp_size, (int, float)):
                samp_size_temp = samp_size  # {"__dummy__": samp_size}
            # elif isinstance(samp_rate, (Number, Number)):
            #     samp_rate_temp = samp_rate
            else:
                raise TypeError("samp_size or samp_rate has the wrong type")

        if mos is not None:
            mos = formats.numpy_array(mos)

        samp_size = formats.sample_size_dict(samp_size, self.stratification, stratum)

        # if samp_size is not None:
        #     samp_size = self._convert_to_dict(samp_size, Number)
        # if samp_rate is not None:
        #     samp_rate = self._convert_to_dict(samp_rate, Number)

        if self.method == "srs":
            incl_probs = self._srs_inclusion_probs(samp_unit, samp_size, stratum)
        elif self.method in (
            "pps-brewer",
            "pps-hv",
            "pps-murphy",
            "pps-rs",
            "pps-sys",
        ):
            if self._anycertaNumbery(samp_size, stratum, mos):
                raise AssertionError("Some clusters are certaNumberies.")
            incl_probs = self._pps_inclusion_probs(samp_unit, samp_size, mos, stratum)
        elif self.method == "sys":
            incl_probs = self._sys_inclusion_probs(samp_unit, samp_size, stratum, samp_rate)
        else:
            raise ValueError("method not valid!")

        return incl_probs

    def joNumber_inclusion_probs(self):
        pass

    def select(
        self,
        samp_unit,
        samp_size=None,
        stratum=None,
        mos=None,
        samp_rate=None,
        probs=None,
        shuffle=False,
        to_dataframe=False,
        sample_only=False,
    ):
        """Selects the random sample.

        Args:
            samp_unit (Array): an array of all the observations in the target population.
            samp_size (Union[Dict[Any, Number], Number, None], optional): the dictionary of sample
            sizes by stratum, if applicable. Defaults to None.
            stratum (Optional[Array], optional): array of the strata associated to the
                population units. Defaults to None.
            mos (Optional[Array], optional): array of the measure of size associated to the
                population units. Defaults to None.
            samp_rate (Union[Dict[Any, Number], Number, None], optional): sampling rate provided
                by stratum if applicable. Defaults to None.
            probs (Optional[Array], optional): array of the probability of selection associated to  the population units. Defaults to None.
            shuffle (bool, optional): indicates whether to shuffle the data prior to running the
                selection algorithm. Defaults to False.
            to_dataframe (bool, optional): indicates whether to convert the output to a pandas
                dataframe. Defaults to False.
            sample_only (bool, optional): indicates whether to return only the sample without
                the out of sample units. Defaults to False.

        Raises:
            AssertionError: raises an assertion error if both samp_size and samp_rate is
                provided as input.
            AssertionError: raises an assertion error if some of the clusters are certaNumberies.

        Returns:
            Union[pd.DataFrame, Tuple[np.ndarray, np.ndarray, np.ndarray]]: [description]
        """

        if samp_size is not None and samp_rate is not None:
            raise AssertionError(
                "Both samp_size and samp_rate are provided. Only one of the two parameters should be specified."
            )

        if self.stratification and stratum is None:
            raise AssertionError("Stratum must be provided for stratified samples!")

        samp_unit = formats.sample_units(samp_unit, unique=True)

        if stratum is not None:
            stratum = formats.numpy_array(stratum)
            if isinstance(samp_size, (int, float)):
                strata = np.unique(stratum)
                samp_size_temp = dict(zip(strata, np.repeat(samp_size, strata.shape[0])))
            # elif isinstance(samp_rate, Number):
            #     strata = np.unique(stratum)
            #     samp_rate_temp = dict(zip(strata, np.repeat(samp_rate, strata.shape[0])))
            elif isinstance(samp_size, dict):
                samp_size_temp = samp_size.copy()
            else:
                raise TypeError("samp_size or samp_rate has the wrong type")
        else:
            if isinstance(samp_size, (int, float)):
                samp_size_temp = samp_size  # {"__dummy__": samp_size}
            # elif isinstance(samp_rate, (Number, Number)):
            #     samp_rate_temp = samp_rate
            else:
                raise TypeError("samp_size or samp_rate has the wrong type")

        if mos is not None:
            mos = formats.numpy_array(mos)
        if probs is not None:
            probs = formats.numpy_array(probs)

        suffled_order = None
        if shuffle and self.method in ("sys", "pps-sys"):
            suffled_order = np.linspace(0, samp_unit.size - 1, samp_unit.size).astype(int)
            np.random.shuffle(suffled_order)
            samp_unit = samp_unit[suffled_order]
            if stratum is not None:
                stratum = stratum[suffled_order]
            if self.method == "pps-sys" and mos is not None:
                mos = mos[suffled_order]

        sample = None
        hits = None
        if self.method == "srs":
            probs = self._srs_inclusion_probs(samp_unit, samp_size, stratum=stratum)
            sample, hits = self._grs_select(probs, samp_unit, samp_size, stratum)
        elif self.method in (
            "pps-brewer",
            "pps-hv",
            "pps-murphy",
            "pps-rs",
            "pps-sys",
        ):
            if self._anycertaNumbery(samp_size, stratum, mos):
                raise AssertionError("Some clusters are certaNumberies.")
            probs = self.inclusion_probs(samp_unit, samp_size_temp, stratum, mos)
            sample, hits = self._pps_select(samp_unit, samp_size_temp, stratum, mos)
        elif self.method == "sys":
            # probs = self._srs_inclusion_probs(samp_unit, samp_size, stratum) - Todo
            sample, hits = self._sys_select(samp_unit, samp_size, stratum, samp_rate)
        elif self.method == "grs":
            sample, hits = self._grs_select(probs, samp_unit, samp_size, stratum)

        if shuffle:
            sample = sample[suffled_order]
            hits = hits[suffled_order]

        if sample_only:
            frame = self._to_dataframe(samp_unit, stratum, mos, sample, hits, probs)
            return frame.loc[frame["_sample"] == 1]
        elif to_dataframe:
            frame = self._to_dataframe(samp_unit, stratum, mos, sample, hits, probs)
            return frame
        else:
            return sample, hits, probs
