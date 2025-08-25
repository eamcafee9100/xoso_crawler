from .base import BaseMakeResult, BasePredictionMethod


class Btl_SC_QM_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_01"

    def get_name(self):
        return "SC_QM 01"

    def get_description(self):
        return "Tổng từ giải 2.2.2 + 5.1.4 + 5.2.4 và giải 1.1.5 + 5.5.2 + 5.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 1), ("giai_5_1", 3), ("giai_5_2", 3)],
            [("giai_1", 4), ("giai_5_5", 1), ("giai_5_6", 3)],
            reverse=True,
        )


class Btl_SC_QM_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_02"

    def get_name(self):
        return "SC_QM 02"

    def get_description(self):
        return "Tổng từ giải 3.1.2 + 3.2.5 + 6.3.3 và giải 3.5.2 + 3.6.4 + 4.2.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 1), ("giai_3_2", 4), ("giai_6_3", 2)],
            [("giai_3_5", 1), ("giai_3_6", 3), ("giai_4_2", 3)],
            reverse=True,
        )


class Btl_SC_QM_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_03"

    def get_name(self):
        return "SC_QM 03"

    def get_description(self):
        return "Tổng từ giải 5.1.3 + 5.2.4 + 5.6.4 và giải 6.1.1 + 5.5.2 + 5.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_1", 2), ("giai_5_2", 3), ("giai_5_6", 3)],
            [("giai_6_1", 0), ("giai_5_5", 1), ("giai_5_6", 3)],
            reverse=True,
        )


class Btl_SC_QM_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_04"

    def get_name(self):
        return "SC_QM 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải 3.1.3 + 3.3.2 + 6.2.3 và giải 3.4.2 + 3.4.4 + 2.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 2), ("giai_3_3", 1), ("giai_6_2", 2)],
            [("giai_3_4", 1), ("giai_3_4", 3), ("giai_2_2", 2)],
            reverse=True,
        )


class Btl_SC_QM_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_05"

    def get_name(self):
        return "SC_QM 05"

    def get_description(self):
        return "Tổng từ giải giai_db.2 + 3.2.3 + 3.3.2 và giải 1.1.2 + 3.5.4 + 3.5.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 1), ("giai_3_2", 2), ("giai_3_3", 1)],
            [("giai_1", 1), ("giai_3_5", 3), ("giai_3_5", 4)],
            reverse=True,
        )


class Btl_SC_QM_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_06"

    def get_name(self):
        return " SC_QM 06 đb"

    def get_description(self):
        return "Tổng từ giải 5.3.3 + 5.3.4 + 7.2.2 và giải 5.5.1 + 5.6.1 + 6.1.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_3", 2), ("giai_5_3", 3), ("giai_7_2", 1)],
            [("giai_5_5", 0), ("giai_5_6", 0), ("giai_6_1", 1)],
            reverse=True,
        )


class Btl_SC_QM_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_07"

    def get_name(self):
        return " SC_QM 07 đb"

    def get_description(self):
        return "Tổng từ giải 3.3.1 + 3.3.5 + 5.6.1 và giải 3.6.1 + 3.6.4 + 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_3", 0), ("giai_3_3", 4), ("giai_5_6", 0)],
            [("giai_3_6", 0), ("giai_3_6", 3), ("giai_5_6", 2)],
            reverse=True,
        )


class Btl_SC_QM_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_08"

    def get_name(self):
        return " SC_QM 08 k3n"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.1.2 + 3.4.1 và giải 3.1.4 + 3.1.5 + 3.4.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_1", 1), ("giai_3_4", 0)],
            [("giai_3_1", 3), ("giai_3_1", 4), ("giai_3_4", 4)],
            reverse=True,
        )


class Btl_SC_QM_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_09"

    def get_name(self):
        return " SC_QM 09"

    def get_description(self):
        return "Tổng từ giải giai_db.3 + 3.3.1 + 3.3.4 và giải 2.1.3 + 3.4.1 + 3.6.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2), ("giai_3_3", 0), ("giai_3_3", 3)],
            [("giai_2_1", 2), ("giai_3_4", 0), ("giai_3_6", 1)],
            reverse=True,
        )


class Btl_SC_QM_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_10"

    def get_name(self):
        return "SC_QM 10 đb"

    def get_description(self):
        return "Tổng từ giải giai_db.1 + 3.1.3 + 3.3.5 và giải 3.1.1 + 3.4.1 + 3.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 0), ("giai_3_1", 2), ("giai_3_3", 4)],
            [("giai_3_1", 0), ("giai_3_4", 0), ("giai_3_6", 2)],
            reverse=True,
        )


class Btl_SC_QM_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_11"

    def get_name(self):
        return "SC_QM 11"

    def get_description(self):
        return "Tổng từ giải 3.1.5 + 3.2.3 + 7.3.2 và giải 3.3.1 + 3.4.5 + 3.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 4), ("giai_3_2", 2), ("giai_7_3", 1)],
            [("giai_3_3", 0), ("giai_3_4", 4), ("giai_3_6", 3)],
            reverse=True,
        )


class Btl_SC_QM_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_12"

    def get_name(self):
        return "SC_QM 12"

    def get_description(self):
        return "Tổng từ giải 4.2.2 + 5.2.2 + 5.2.4 và giải 5.1.4 + 5.5.3 + 5.5.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_2", 1), ("giai_5_2", 1), ("giai_5_2", 3)],
            [("giai_5_1", 3), ("giai_5_5", 2), ("giai_5_5", 3)],
            reverse=True,
        )


class Btl_SC_QM_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_13"

    def get_name(self):
        return "SC_QM 13"

    def get_description(self):
        return "Tổng từ giải 1.1.1 + 3.2.2 + 3.2.4 và giải giai_db.2 + 3.6.1 + 3.6.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 0), ("giai_3_2", 1), ("giai_3_2", 3)],
            [("giai_db", 1), ("giai_3_6", 0), ("giai_3_6", 1)],
            reverse=True,
        )


class Btl_SC_QM_14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_14"

    def get_name(self):
        return "Bạch thủ lô SC_QM 14"

    def get_description(self):
        return "Tổng từ giải 3.2.3 + 3.3.2 + 5.3.2 và giải 3.6.2 + 3.6.3 + 4.4.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 2), ("giai_3_3", 1), ("giai_5_3", 1)],
            [("giai_3_6", 1), ("giai_3_6", 2), ("giai_4_4", 3)],
            reverse=True,
        )


class Btl_SC_QM_15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_15"

    def get_name(self):
        return "Bạch thủ lô SC_QM 15"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.3.5 + 4.3.2 và giải giai_db.2 + 3.4.4 + 3.6.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_3", 4), ("giai_4_3", 1)],
            [("giai_db", 1), ("giai_3_4", 3), ("giai_3_6", 4)],
            reverse=True,
        )


class Btl_SC_QM_16LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_16"

    def get_name(self):
        return "Bạch thủ lô SC_QM 16"

    def get_description(self):
        return "Tổng từ giải 3.2.2 + 3.3.5 + 6.2.1 và giải 3.6.4 + 3.6.5 + 6.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 1), ("giai_3_3", 4), ("giai_6_2", 0)],
            [("giai_3_6", 3), ("giai_3_6", 4), ("giai_6_2", 2)],
            reverse=True,
        )


class Btl_SC_QM_17LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_qm_17"

    def get_name(self):
        return "Bạch thủ lô SC_QM 17 db"

    def get_description(self):
        return "Tổng từ giải 1.1.4 + 3.1.5 + 3.2.3 và giải giai_db.1 + 3.4.1 + 3.4.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 3), ("giai_3_1", 4), ("giai_3_2", 2)],
            [("giai_db", 0), ("giai_3_4", 0), ("giai_3_4", 1)],
            reverse=True,
        )
